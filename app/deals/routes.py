from flask import Blueprint, request, jsonify
from app import db
from app.models import Deal, Installment, Payment, PaymentAllocation
from app.utils.interest_calculations import update_accrued_interest, allocate_payment_to_installments, allocate_payment_across_deals
from sqlalchemy import func
from datetime import datetime, timedelta

bp = Blueprint('deals', __name__)


@bp.route('/deals', methods=['POST'])
def create_deal():
    """Create a new deal/loan"""
    try:
        data = request.get_json()
        
        # Create deal (deal_id will be auto-generated)
        deal = Deal(
            customer_name=data['customer_name'],
            dealer_id=data.get('dealer_id'),
            total_amount=data['total_amount'],
            interest_percentage=data.get('interest_percentage', 0),
            deal_date=datetime.strptime(data['deal_date'], '%Y-%m-%d').date(),
            status='active'
        )
        db.session.add(deal)
        db.session.flush()
        
        # Create installments if provided
        if 'installments' in data and data['installments']:
            for inst_data in data['installments']:
                installment = Installment(
                    deal_id=deal.deal_id,
                    due_date=datetime.strptime(inst_data['due_date'], '%Y-%m-%d').date(),
                    days=inst_data.get('days', 0),
                    percentage=inst_data.get('percentage', 0),
                    amount=inst_data['amount'],
                    pending_amount=inst_data['amount']
                )
                db.session.add(installment)
        
        db.session.commit()
        
        # Update accrued interest (will be 0 for new deal, but ensures interest row exists)
        update_accrued_interest(deal.deal_id)
        
        # Refresh to get updated data
        db.session.refresh(deal)
        
        return jsonify(deal.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@bp.route('/deals', methods=['GET'])
def get_deals():
    """Get all deals with optional filters"""
    try:
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        customer_name = request.args.get('customer_name')
        deal_id = request.args.get('deal_id')
        status = request.args.get('status')
        dealer_id = request.args.get('dealer_id')
        
        query = Deal.query
        
        if date_from:
            query = query.filter(Deal.deal_date >= datetime.strptime(date_from, '%Y-%m-%d').date())
        if date_to:
            query = query.filter(Deal.deal_date <= datetime.strptime(date_to, '%Y-%m-%d').date())
        if customer_name:
            query = query.filter(Deal.customer_name.ilike(f'%{customer_name}%'))
        if deal_id:
            query = query.filter(Deal.deal_id == int(deal_id))
        if status:
            query = query.filter(Deal.status == status)
        if dealer_id:
            query = query.filter(Deal.dealer_id == dealer_id)
        
        deals = query.order_by(Deal.deal_date.desc()).all()
        
        # Update accrued interest for each deal before returning
        for deal in deals:
            update_accrued_interest(deal.deal_id)
        
        # Refresh deals to get updated data
        for deal in deals:
            db.session.refresh(deal)
        
        return jsonify([deal.to_dict() for deal in deals]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/deals/<int:deal_id>', methods=['GET'])
def get_deal(deal_id):
    """Get deal details with installments and payments"""
    try:
        deal = Deal.query.get_or_404(deal_id)
        
        # Update accrued interest before returning
        update_accrued_interest(deal.deal_id)
        
        # Refresh to get updated data
        db.session.refresh(deal)
        
        return jsonify(deal.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@bp.route('/deals/<int:deal_id>', methods=['PUT'])
def update_deal(deal_id):
    """Update deal details"""
    try:
        deal = Deal.query.get_or_404(deal_id)
        data = request.get_json()
        
        if 'customer_name' in data:
            deal.customer_name = data['customer_name']
        if 'dealer_id' in data:
            deal.dealer_id = data['dealer_id']
        if 'total_amount' in data:
            deal.total_amount = data['total_amount']
        if 'interest_percentage' in data:
            deal.interest_percentage = data['interest_percentage']
        if 'deal_date' in data:
            deal.deal_date = datetime.strptime(data['deal_date'], '%Y-%m-%d').date()
        if 'status' in data:
            deal.status = data['status']
        
        db.session.commit()
        
        # Update accrued interest after changes
        update_accrued_interest(deal.deal_id)
        db.session.refresh(deal)
        
        return jsonify(deal.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@bp.route('/deals/<int:deal_id>/installments', methods=['POST'])
def create_installments(deal_id):
    """Create installments for a deal"""
    try:
        deal = Deal.query.get_or_404(deal_id)
        data = request.get_json()
        
        installments_data = data.get('installments', [])
        
        for inst_data in installments_data:
            installment = Installment(
                deal_id=deal.deal_id,
                due_date=datetime.strptime(inst_data['due_date'], '%Y-%m-%d').date(),
                days=inst_data.get('days', 0),
                percentage=inst_data.get('percentage', 0),
                amount=inst_data['amount'],
                pending_amount=inst_data['amount']
            )
            db.session.add(installment)
        
        db.session.commit()
        
        # Update accrued interest
        update_accrued_interest(deal.deal_id)
        db.session.refresh(deal)
        
        return jsonify(deal.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@bp.route('/deals/<int:deal_id>/payments', methods=['POST'])
def add_payment(deal_id):
    """Add a payment and allocate it to installments.
    
    If cross_deal flag is set to true, payment will be allocated across all active deals
    for the same dealer and customer, with oldest deal getting priority first.
    """
    try:
        deal = Deal.query.get_or_404(deal_id)
        data = request.get_json()
        
        payment_amount = data['amount']
        payment_date = datetime.strptime(data['payment_date'], '%Y-%m-%d').date()
        
        # Check if cross-deal allocation is requested
        cross_deal = data.get('cross_deal', False)
        
        if cross_deal and deal.dealer_id and deal.customer_name:
            # Allocate across all deals for this dealer and customer
            result = allocate_payment_across_deals(
                deal.dealer_id, 
                deal.customer_name, 
                payment_amount, 
                payment_date
            )
            
            if result is None:
                return jsonify({'error': 'Failed to allocate payment across deals'}), 400
            
            # Get all affected deals
            deals = Deal.query.filter(
                Deal.dealer_id == deal.dealer_id,
                Deal.customer_name == deal.customer_name,
                Deal.status == 'active'
            ).all()
            
            # Refresh all deals to get updated data
            for d in deals:
                db.session.refresh(d)
            
            return jsonify({
                'message': 'Cross-deal payment added successfully',
                'allocation': result,
                'deals': [d.to_dict() for d in deals]
            }), 201
        else:
            # Original single-deal allocation
            result = allocate_payment_to_installments(deal.deal_id, payment_amount, payment_date)
            
            if result is None:
                return jsonify({'error': 'Failed to allocate payment'}), 400
            
            # Refresh deal to get updated data
            db.session.refresh(deal)
            
            return jsonify({
                'message': 'Payment added successfully',
                'allocation': result,
                'deal': deal.to_dict()
            }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@bp.route('/deals/payments/cross-deal', methods=['POST'])
def add_cross_deal_payment():
    """
    Add a payment that can be allocated across multiple deals for the same dealer and customer.
    Priority: Oldest deal first (5% deal before 10% deal).
    
    Request body:
    {
        "dealer_id": "uuid-of-dealer",
        "customer_name": "Customer Name",
        "amount": 15000,
        "payment_date": "2024-01-15"
    }
    """
    try:
        data = request.get_json()
        
        dealer_id = data.get('dealer_id')
        customer_name = data.get('customer_name')
        payment_amount = data['amount']
        payment_date = datetime.strptime(data['payment_date'], '%Y-%m-%d').date()
        
        if not dealer_id or not customer_name:
            return jsonify({'error': 'dealer_id and customer_name are required'}), 400
        
        # Allocate payment across deals
        result = allocate_payment_across_deals(dealer_id, customer_name, payment_amount, payment_date)
        
        if result is None:
            return jsonify({'error': 'No active deals found for this dealer and customer'}), 400
        
        # Get all affected deals
        deals = Deal.query.filter(
            Deal.dealer_id == dealer_id,
            Deal.customer_name == customer_name,
            Deal.status == 'active'
        ).all()
        
        # Refresh all deals to get updated data
        for deal in deals:
            db.session.refresh(deal)
        
        return jsonify({
            'message': 'Cross-deal payment added successfully',
            'allocation': result,
            'deals': [deal.to_dict() for deal in deals]
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@bp.route('/deals/<int:deal_id>/ledger', methods=['GET'])
def get_deal_ledger(deal_id):
    """Get complete ledger for a deal (installments + payments)"""
    try:
        deal = Deal.query.get_or_404(deal_id)
        
        # Update accrued interest
        update_accrued_interest(deal.deal_id)
        db.session.refresh(deal)
        
        # Build ledger entries
        ledger = []
        
        # Add installments
        for idx, inst in enumerate(deal.installments, 1):
            ledger.append({
                'date': inst.due_date.isoformat(),
                'type': 'installment',
                'description': f"Installment #{idx} - Due",
                'amount': float(inst.amount),
                'pending': float(inst.pending_amount),
                'days': inst.days,
                'percentage': float(inst.percentage) if inst.percentage else 0,
                'id': str(inst.id)
            })
        
        # Add payments
        for payment in deal.payments:
            ledger.append({
                'date': payment.payment_date.isoformat(),
                'type': 'payment',
                'description': f"Payment - {payment.remark or 'No remark'}",
                'amount': -float(payment.amount),  # Negative for payment
                'id': str(payment.id)
            })
        
        # Sort by date
        ledger.sort(key=lambda x: x['date'])
        
        # Calculate running balance
        balance = float(deal.total_amount)
        for entry in ledger:
            if entry['type'] == 'installment':
                balance = entry['pending']
            elif entry['type'] == 'payment':
                balance -= abs(entry['amount'])
            entry['balance'] = balance
        
        return jsonify({
            'deal': deal.to_dict(),
            'ledger': ledger
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
