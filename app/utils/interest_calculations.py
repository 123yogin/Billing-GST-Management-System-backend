from datetime import date
from decimal import Decimal
from app import db
from app.models import Deal, Installment, Payment, PaymentAllocation


def calculate_payment_interest(payment_amount, payment_date, due_date, interest_rate):
    """
    Calculate interest on a payment when it's late.
    
    Args:
        payment_amount: Amount being paid
        payment_date: Date of payment
        due_date: Original due date
        interest_rate: Annual interest percentage
    
    Returns:
        Interest amount (0 if payment is on time or early)
    """
    if interest_rate <= 0:
        return Decimal('0')
    
    days_diff = (payment_date - due_date).days
    
    if days_diff > 0:
        interest = (Decimal(str(payment_amount)) * Decimal(str(interest_rate)) * Decimal(str(days_diff))) / (Decimal('365') * Decimal('100'))
        return interest
    
    return Decimal('0')


def update_accrued_interest(deal_id):
    """
    Calculate and update accrued interest for all overdue unpaid installments.
    This creates/updates an 'interest' type installment row.
    
    Returns:
        Total accrued interest amount
    """
    today = date.today()
    deal = Deal.query.get(deal_id)
    
    if not deal or deal.interest_percentage <= 0:
        return Decimal('0')
    
    rate = Decimal(str(deal.interest_percentage))
    total_accrued_interest = Decimal('0')
    
    # Get all unpaid, overdue installments (pending_amount > 0 means unpaid)
    overdue_installments = Installment.query.filter(
        Installment.deal_id == deal_id,
        Installment.pending_amount > 0,
        Installment.due_date < today
    ).all()
    
    for inst in overdue_installments:
        days_overdue = (today - inst.due_date).days
        if days_overdue > 0 and inst.pending_amount > 0:
            interest = (Decimal(str(inst.pending_amount)) * rate * Decimal(str(days_overdue))) / (Decimal('365') * Decimal('100'))
            total_accrued_interest += interest
    
    # Note: Interest tracking is now handled separately if needed
    # For now, we'll skip creating a separate interest installment row
    # as the type field has been removed. Interest can be calculated on-the-fly.
    
    db.session.commit()
    return total_accrued_interest


def allocate_payment_to_installments(deal_id, payment_amount, payment_date):
    """
    Allocate payment to installments sequentially (oldest first).
    Also calculates realized interest for each allocation.
    
    Args:
        deal_id: UUID of the deal
        payment_amount: Total payment amount
        payment_date: Date of payment
    
    Returns:
        dict with allocation details and total interest realized
    """
    deal = Deal.query.get(deal_id)
    if not deal:
        return None
    
    remaining_amount = Decimal(str(payment_amount))
    total_interest_realized = Decimal('0')
    allocations = []
    
    # Get unpaid installments ordered by due_date (oldest first)
    # pending_amount > 0 means unpaid
    unpaid_installments = Installment.query.filter(
        Installment.deal_id == deal_id,
        Installment.pending_amount > 0
    ).order_by(Installment.due_date.asc()).all()
    
    # Create payment record
    payment = Payment(
        deal_id=deal_id,
        payment_date=payment_date,
        amount=float(payment_amount),
        type='installment'
    )
    db.session.add(payment)
    db.session.flush()
    
    # Allocate to each installment
    for inst in unpaid_installments:
        if remaining_amount <= 0:
            break
        
        if inst.pending_amount <= 0:
            continue
        
        # Calculate how much to allocate
        allocate_amount = min(remaining_amount, Decimal(str(inst.pending_amount)))
        
        # Calculate realized interest if late
        interest_realized = Decimal('0')
        if payment_date > inst.due_date:
            interest_realized = calculate_payment_interest(
                float(allocate_amount),
                payment_date,
                inst.due_date,
                deal.interest_percentage
            )
            total_interest_realized += interest_realized
        
        # Update installment
        inst.pending_amount = float(Decimal(str(inst.pending_amount)) - allocate_amount)
        
        # Create allocation record
        allocation = PaymentAllocation(
            payment_id=payment.id,
            installment_id=inst.id,
            allocated_amount=float(allocate_amount),
            interest_amount=float(interest_realized)
        )
        db.session.add(allocation)
        allocations.append({
            'installment_id': str(inst.id),
            'allocated_amount': float(allocate_amount),
            'interest_realized': float(interest_realized)
        })
        
        remaining_amount -= allocate_amount
    
    # Update payment remark with interest info
    if total_interest_realized > 0:
        payment.remark = f"Interest realized: {float(total_interest_realized):.2f}"
    
    db.session.commit()
    
    # Update accrued interest after payment
    update_accrued_interest(deal_id)
    
    return {
        'payment_id': str(payment.id),
        'allocations': allocations,
        'total_interest_realized': float(total_interest_realized),
        'remaining_amount': float(remaining_amount) if remaining_amount > 0 else 0
    }
