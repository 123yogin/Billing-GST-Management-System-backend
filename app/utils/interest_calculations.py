from datetime import date, timedelta, datetime
from decimal import Decimal
from app import db
from app.models import Deal, Installment, Payment, PaymentAllocation
from config import Config

# 10-day buffer period where no interest is charged
BUFFER_DAYS = 10


def get_ist_date():
    """
    Get current date in Indian Standard Time (IST).
    
    Returns:
        date object representing today's date in IST
    """
    ist_now = datetime.now(Config.IST_TIMEZONE)
    return ist_now.date()


def get_ist_datetime():
    """
    Get current datetime in Indian Standard Time (IST).
    
    Returns:
        datetime object representing current time in IST
    """
    return datetime.now(Config.IST_TIMEZONE)


def check_and_close_deal_if_paid(deal_id):
    """
    Check if all installments for a deal are fully paid.
    If yes, update the deal status to 'closed'.
    
    Args:
        deal_id: ID of the deal to check
    
    Returns:
        True if deal was closed, False otherwise
    """
    deal = Deal.query.get(deal_id)
    if not deal:
        return False
    
    # Check if deal is already closed
    if deal.status == 'closed':
        return False
    
    # Get all installments for this deal
    all_installments = Installment.query.filter(
        Installment.deal_id == deal_id
    ).all()
    
    # If no installments exist, don't close the deal
    if not all_installments:
        return False
    
    # Check if all installments are fully paid (pending_amount <= 0)
    all_paid = all(
        float(inst.pending_amount) <= 0 
        for inst in all_installments
    )
    
    if all_paid:
        deal.status = 'closed'
        db.session.commit()
        return True
    
    return False


def get_last_payment_date_for_installment(installment_id):
    """
    Get the last payment date for an installment.
    Returns None if no payment has been made.
    
    Args:
        installment_id: UUID of the installment
    
    Returns:
        Date of last payment or None
    """
    last_payment = db.session.query(Payment.payment_date).join(
        PaymentAllocation
    ).filter(
        PaymentAllocation.installment_id == installment_id
    ).order_by(
        Payment.payment_date.desc()
    ).first()
    
    return last_payment[0] if last_payment else None


def calculate_payment_interest(payment_amount, payment_date, start_date, due_date, interest_rate, buffer_days=BUFFER_DAYS):
    """
    Calculate interest on a payment from the start date.
    Interest accrues normally until due_date, then there's a buffer period after due_date where no interest is charged.
    
    Args:
        payment_amount: Amount being paid
        payment_date: Date of payment
        start_date: Start date for interest calculation (deal_date or last payment date)
        due_date: Due date of the installment (buffer period starts after this)
        interest_rate: Annual interest percentage
        buffer_days: Number of buffer days where no interest is charged after due_date (default: 10)
    
    Returns:
        Interest amount calculated, accounting for buffer period after due_date
    """
    if interest_rate <= 0:
        return Decimal('0')
    
    # Interest accrues normally from start_date to due_date
    # Buffer period: from due_date to (due_date + buffer_days) - no interest
    # After buffer period: interest resumes
    
    buffer_end_date = due_date + timedelta(days=buffer_days)
    
    # Case 1: Payment before or on due_date - calculate interest normally
    if payment_date <= due_date:
        # Calculate days from start_date to payment_date (inclusive)
        days_diff = (payment_date - start_date).days + 1
        if days_diff > 0:
            interest = (Decimal(str(payment_amount)) * Decimal(str(interest_rate)) * Decimal(str(days_diff))) / (Decimal('365') * Decimal('100'))
            return interest
        return Decimal('0')
    
    # Case 2: Payment during buffer period (after due_date but before buffer_end_date) - no interest
    if payment_date <= buffer_end_date:
        # Calculate interest only up to due_date
        days_diff = (due_date - start_date).days + 1
        if days_diff > 0:
            interest = (Decimal(str(payment_amount)) * Decimal(str(interest_rate)) * Decimal(str(days_diff))) / (Decimal('365') * Decimal('100'))
            return interest
        return Decimal('0')
    
    # Case 3: Payment after buffer period - calculate interest up to due_date, include buffer days, then from buffer_end_date to payment_date
    # Interest from start_date to due_date
    days_to_due = (due_date - start_date).days + 1
    interest_to_due = Decimal('0')
    if days_to_due > 0:
        interest_to_due = (Decimal(str(payment_amount)) * Decimal(str(interest_rate)) * Decimal(str(days_to_due))) / (Decimal('365') * Decimal('100'))
    
    # Include buffer days in interest calculation (treat as if interest was accruing during buffer)
    interest_for_buffer = Decimal('0')
    if buffer_days > 0:
        interest_for_buffer = (Decimal(str(payment_amount)) * Decimal(str(interest_rate)) * Decimal(str(buffer_days))) / (Decimal('365') * Decimal('100'))
    
    # Interest from buffer_end_date to payment_date
    days_after_buffer = (payment_date - buffer_end_date).days + 1
    interest_after_buffer = Decimal('0')
    if days_after_buffer > 0:
        interest_after_buffer = (Decimal(str(payment_amount)) * Decimal(str(interest_rate)) * Decimal(str(days_after_buffer))) / (Decimal('365') * Decimal('100'))
    
    return interest_to_due + interest_for_buffer + interest_after_buffer


def update_accrued_interest(deal_id):
    """
    Calculate accrued interest for all unpaid installments.
    Interest accrues normally until due_date, then there's a buffer period after due_date where no interest is charged.
    Uses IST (Indian Standard Time) for date calculations.
    
    Returns:
        Total accrued interest amount
    """
    today = get_ist_date()  # Use IST date instead of system date
    deal = Deal.query.get(deal_id)
    
    if not deal or deal.interest_percentage <= 0:
        return Decimal('0')
    
    rate = Decimal(str(deal.interest_percentage))
    total_accrued_interest = Decimal('0')
    
    # Get all unpaid installments (pending_amount > 0 means unpaid)
    unpaid_installments = Installment.query.filter(
        Installment.deal_id == deal_id,
        Installment.pending_amount > 0
    ).all()
    
    for inst in unpaid_installments:
        if inst.pending_amount > 0:
            # Get the last payment date for this installment
            last_payment_date = get_last_payment_date_for_installment(inst.id)
            
            # Use last payment date if available, otherwise use deal_date
            base_date = last_payment_date if last_payment_date else deal.deal_date
            
            due_date = inst.due_date
            buffer_end_date = due_date + timedelta(days=BUFFER_DAYS)
            
            # Case 1: Today is before or on due_date - calculate interest normally
            if today <= due_date:
                days_diff = (today - base_date).days + 1
                if days_diff > 0:
                    interest = (Decimal(str(inst.pending_amount)) * rate * Decimal(str(days_diff))) / (Decimal('365') * Decimal('100'))
                    total_accrued_interest += interest
            
            # Case 2: Today is during buffer period - calculate interest only up to due_date
            elif today <= buffer_end_date:
                days_diff = (due_date - base_date).days + 1
                if days_diff > 0:
                    interest = (Decimal(str(inst.pending_amount)) * rate * Decimal(str(days_diff))) / (Decimal('365') * Decimal('100'))
                    total_accrued_interest += interest
            
            # Case 3: Today is after buffer period - calculate interest up to due_date + buffer days + from buffer_end_date to today
            else:
                # Interest from base_date to due_date
                days_to_due = (due_date - base_date).days + 1
                interest_to_due = Decimal('0')
                if days_to_due > 0:
                    interest_to_due = (Decimal(str(inst.pending_amount)) * rate * Decimal(str(days_to_due))) / (Decimal('365') * Decimal('100'))
                
                # Include buffer days in interest calculation (treat as if interest was accruing during buffer)
                interest_for_buffer = Decimal('0')
                if BUFFER_DAYS > 0:
                    interest_for_buffer = (Decimal(str(inst.pending_amount)) * rate * Decimal(str(BUFFER_DAYS))) / (Decimal('365') * Decimal('100'))
                
                # Interest from buffer_end_date to today
                days_after_buffer = (today - buffer_end_date).days + 1
                interest_after_buffer = Decimal('0')
                if days_after_buffer > 0:
                    interest_after_buffer = (Decimal(str(inst.pending_amount)) * rate * Decimal(str(days_after_buffer))) / (Decimal('365') * Decimal('100'))
                
                total_accrued_interest += interest_to_due + interest_for_buffer + interest_after_buffer
    
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
        
        # Get the last payment date for this installment to calculate interest correctly
        last_payment_date = get_last_payment_date_for_installment(inst.id)
        # Use last payment date if available, otherwise use deal_date
        interest_base_date = last_payment_date if last_payment_date else deal.deal_date
        
        # Calculate realized interest from the base date (last payment or deal_date)
        # Buffer period starts after the installment's due_date
        interest_realized = calculate_payment_interest(
            float(allocate_amount),
            payment_date,
            interest_base_date,
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
    payment.remark = f"Interest realized: {float(total_interest_realized):.2f}"
    
    db.session.commit()
    
    # Update accrued interest after payment
    update_accrued_interest(deal_id)
    
    # Check if deal is fully paid and close it if so
    check_and_close_deal_if_paid(deal_id)
    
    return {
        'payment_id': str(payment.id),
        'allocations': allocations,
        'total_interest_realized': float(total_interest_realized),
        'remaining_amount': float(remaining_amount) if remaining_amount > 0 else 0
    }


def allocate_payment_across_deals(dealer_id, customer_name, payment_amount, payment_date):
    """
    Allocate payment across multiple deals for the same dealer and customer.
    Priority: Oldest deal first (by deal_date), then by deal_id.
    
    This ensures that when a customer pays, the payment first goes to the oldest deal
    (e.g., 5% interest deal) and any extra money goes to newer deals (e.g., 10% interest deal).
    
    Args:
        dealer_id: UUID of the dealer
        customer_name: Name of the customer
        payment_amount: Total payment amount
        payment_date: Date of payment
    
    Returns:
        dict with allocation details across all deals
    """
    remaining_amount = Decimal(str(payment_amount))
    total_allocations = []
    all_payments = []
    
    # Find all active deals for this dealer and customer
    # Order by deal_date (oldest first), then by deal_id
    deals = Deal.query.filter(
        Deal.dealer_id == dealer_id,
        Deal.customer_name == customer_name,
        Deal.status == 'active'
    ).order_by(Deal.deal_date.asc(), Deal.deal_id.asc()).all()
    
    if not deals:
        return None
    
    # Allocate payment across deals
    for deal in deals:
        if remaining_amount <= 0:
            break
        
        # Get unpaid installments for this deal
        unpaid_installments = Installment.query.filter(
            Installment.deal_id == deal.deal_id,
            Installment.pending_amount > 0
        ).order_by(Installment.due_date.asc()).all()
        
        if not unpaid_installments:
            continue
        
        # Create payment record for this deal
        payment = Payment(
            deal_id=deal.deal_id,
            payment_date=payment_date,
            amount=0,  # Will be updated after allocation
            type='installment',
            remark=f"Cross-deal payment allocation"
        )
        db.session.add(payment)
        db.session.flush()
        all_payments.append(payment)
        
        deal_allocated = Decimal('0')
        deal_interest = Decimal('0')
        deal_allocations = []
        
        # Allocate to installments within this deal
        for inst in unpaid_installments:
            if remaining_amount <= 0:
                break
            
            if inst.pending_amount <= 0:
                continue
            
            # Calculate how much to allocate
            allocate_amount = min(remaining_amount, Decimal(str(inst.pending_amount)))
            
            # Get the last payment date for this installment to calculate interest correctly
            last_payment_date = get_last_payment_date_for_installment(inst.id)
            # Use last payment date if available, otherwise use deal_date
            interest_base_date = last_payment_date if last_payment_date else deal.deal_date
            
            # Calculate realized interest from the base date (last payment or deal_date)
            # Buffer period starts after the installment's due_date
            interest_realized = calculate_payment_interest(
                float(allocate_amount),
                payment_date,
                interest_base_date,
                inst.due_date,
                deal.interest_percentage
            )
            deal_interest += interest_realized
            
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
            
            deal_allocated += allocate_amount
            remaining_amount -= allocate_amount
            
            deal_allocations.append({
                'installment_id': str(inst.id),
                'allocated_amount': float(allocate_amount),
                'interest_realized': float(interest_realized)
            })
        
        # Update payment amount
        if deal_allocated > 0:
            payment.amount = float(deal_allocated)
            payment.remark = f"Cross-deal payment - Interest: {float(deal_interest):.2f}"
            
            total_allocations.append({
                'deal_id': deal.deal_id,
                'deal_interest_rate': float(deal.interest_percentage),
                'allocated_amount': float(deal_allocated),
                'total_interest_realized': float(deal_interest),
                'allocations': deal_allocations
            })
            
            # Update accrued interest for this deal
            update_accrued_interest(deal.deal_id)
            
            # Check if deal is fully paid and close it if so
            check_and_close_deal_if_paid(deal.deal_id)
        else:
            # No allocation to this deal, remove the payment record
            db.session.delete(payment)
    
    db.session.commit()
    
    return {
        'total_payment': float(Decimal(str(payment_amount))),
        'allocated_amount': float(Decimal(str(payment_amount)) - remaining_amount),
        'remaining_amount': float(remaining_amount) if remaining_amount > 0 else 0,
        'deal_allocations': total_allocations
    }