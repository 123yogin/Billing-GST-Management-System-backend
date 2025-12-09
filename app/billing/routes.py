from flask import Blueprint, request, jsonify, send_file
from app import db
from app.models import FarmerBill, DealerBill, Item
from app.utils.calculations import calculate_farmer_bill_totals, calculate_dealer_bill_totals
from app.utils.pdf_generator import generate_farmer_bill_pdf, generate_dealer_bill_pdf
from datetime import datetime
import uuid

bp = Blueprint('billing', __name__)

# ============ FARMER BILLS ============

@bp.route('/farmer-bills', methods=['POST'])
def create_farmer_bill():
    """Create a new farmer bill"""
    try:
        data = request.get_json()
        
        # Generate bill_id
        bill_id = str(uuid.uuid4())
        
        # Calculate totals
        items_data = data.get('items', [])
        other_expense = data.get('other_expense', 0)
        discount = data.get('discount', 0)
        
        totals = calculate_farmer_bill_totals(items_data, other_expense, discount)
        
        # Create bill
        bill = FarmerBill(
            bill_id=bill_id,
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            customer_name=data['customer_name'],
            other_expense=other_expense,
            discount=discount,
            final_total=totals['final_total'],
            
            # New Fields
            transport_mode=data.get('transport_mode'),
            vehicle_number=data.get('vehicle_number'),
            supply_date=datetime.strptime(data['supply_date'], '%Y-%m-%d') if data.get('supply_date') else None,
            place_of_supply=data.get('place_of_supply'),
            receiver_address=data.get('receiver_address'),
            receiver_state=data.get('receiver_state'),
            receiver_state_code=data.get('receiver_state_code'),
            receiver_gstin=data.get('receiver_gstin')
        )
        db.session.add(bill)
        db.session.flush()
        
        # Create items
        for item_data in items_data:
            item = Item(
                farmer_bill_id=bill.id,
                item=item_data['item'],
                hsn_code=item_data.get('hsn_code'),
                quantity_bags=item_data.get('quantity_bags', 0),
                weight=item_data['weight'],
                price=item_data['price'],
                item_total=item_data['item_total']
            )
            db.session.add(item)
        
        db.session.commit()
        
        return jsonify(bill.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/farmer-bills', methods=['GET'])
def get_farmer_bills():
    """Get all farmer bills with optional filters"""
    try:
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        customer_name = request.args.get('customer_name')
        bill_id = request.args.get('bill_id')
        
        query = FarmerBill.query
        
        if date_from:
            query = query.filter(FarmerBill.date >= datetime.strptime(date_from, '%Y-%m-%d').date())
        if date_to:
            query = query.filter(FarmerBill.date <= datetime.strptime(date_to, '%Y-%m-%d').date())
        if customer_name:
            query = query.filter(FarmerBill.customer_name.ilike(f'%{customer_name}%'))
        if bill_id:
            query = query.filter(FarmerBill.bill_id.ilike(f'%{bill_id}%'))
        
        bills = query.order_by(FarmerBill.date.desc()).all()
        return jsonify([bill.to_dict() for bill in bills]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/farmer-bills/<bill_id>', methods=['GET'])
def get_farmer_bill(bill_id):
    """Get a specific farmer bill by bill_id"""
    try:
        bill = FarmerBill.query.filter_by(bill_id=bill_id).first_or_404()
        return jsonify(bill.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@bp.route('/farmer-bills/<bill_id>/pdf', methods=['GET'])
def get_farmer_bill_pdf(bill_id):
    """Generate PDF for farmer bill"""
    try:
        bill = FarmerBill.query.filter_by(bill_id=bill_id).first_or_404()
        bill_dict = bill.to_dict()
        
        # Format dates and numbers for PDF
        bill_dict['date'] = bill.date.strftime('%Y-%m-%d')
        for item in bill_dict['items']:
            item['weight'] = f"{item['weight']:.2f}"
            item['price'] = f"{item['price']:.2f}"
            item['item_total'] = f"{item['item_total']:.2f}"
        bill_dict['other_expense'] = f"{bill_dict['other_expense']:.2f}"
        bill_dict['discount'] = f"{bill_dict['discount']:.2f}"
        bill_dict['final_total'] = f"{bill_dict['final_total']:.2f}"
        
        pdf_buffer = generate_farmer_bill_pdf(bill_dict)
        pdf_buffer.seek(0)
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'farmer_bill_{bill_id}.pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ============ DEALER BILLS ============

@bp.route('/dealer-bills', methods=['POST'])
def create_dealer_bill():
    """Create a new dealer bill"""
    try:
        data = request.get_json()
        
        # Generate bill_id
        bill_id = str(uuid.uuid4())
        
        # Calculate totals
        items_data = data.get('items', [])
        other_expense = data.get('other_expense', 0)
        discount = data.get('discount', 0)
        gst_percentage = data.get('gst_percentage', 18)
        
        totals = calculate_dealer_bill_totals(items_data, other_expense, discount, gst_percentage)
        
        # Create bill
        bill = DealerBill(
            bill_id=bill_id,
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            customer_name=data['customer_name'],
            other_expense=other_expense,
            discount=discount,
            gst_percentage=gst_percentage,
            gst_amount=totals['gst_amount'],
            sgst=totals['sgst'],
            grand_total=totals['grand_total'],
            
            # New Fields
            transport_mode=data.get('transport_mode'),
            vehicle_number=data.get('vehicle_number'),
            supply_date=datetime.strptime(data['supply_date'], '%Y-%m-%d') if data.get('supply_date') else None,
            place_of_supply=data.get('place_of_supply'),
            receiver_address=data.get('receiver_address'),
            receiver_state=data.get('receiver_state'),
            receiver_state_code=data.get('receiver_state_code'),
            receiver_gstin=data.get('receiver_gstin')
        )
        db.session.add(bill)
        db.session.flush()
        
        # Create items
        for item_data in items_data:
            item = Item(
                dealer_bill_id=bill.id,
                item=item_data['item'],
                hsn_code=item_data.get('hsn_code'),
                quantity_bags=item_data.get('quantity_bags', 0),
                weight=item_data['weight'],
                price=item_data['price'],
                item_total=item_data['item_total']
            )
            db.session.add(item)
        
        db.session.commit()
        
        return jsonify(bill.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/dealer-bills', methods=['GET'])
def get_dealer_bills():
    """Get all dealer bills with optional filters"""
    try:
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        customer_name = request.args.get('customer_name')
        bill_id = request.args.get('bill_id')
        
        query = DealerBill.query
        
        if date_from:
            query = query.filter(DealerBill.date >= datetime.strptime(date_from, '%Y-%m-%d').date())
        if date_to:
            query = query.filter(DealerBill.date <= datetime.strptime(date_to, '%Y-%m-%d').date())
        if customer_name:
            query = query.filter(DealerBill.customer_name.ilike(f'%{customer_name}%'))
        if bill_id:
            query = query.filter(DealerBill.bill_id.ilike(f'%{bill_id}%'))
        
        bills = query.order_by(DealerBill.date.desc()).all()
        return jsonify([bill.to_dict() for bill in bills]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/dealer-bills/<bill_id>', methods=['GET'])
def get_dealer_bill(bill_id):
    """Get a specific dealer bill by bill_id"""
    try:
        bill = DealerBill.query.filter_by(bill_id=bill_id).first_or_404()
        return jsonify(bill.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@bp.route('/dealer-bills/<bill_id>/pdf', methods=['GET'])
def get_dealer_bill_pdf(bill_id):
    """Generate PDF for dealer bill"""
    try:
        bill = DealerBill.query.filter_by(bill_id=bill_id).first_or_404()
        bill_dict = bill.to_dict()
        
        # Format dates and numbers for PDF
        bill_dict['date'] = bill.date.strftime('%Y-%m-%d')
        for item in bill_dict['items']:
            item['weight'] = f"{item['weight']:.2f}"
            item['price'] = f"{item['price']:.2f}"
            item['item_total'] = f"{item['item_total']:.2f}"
        bill_dict['other_expense'] = f"{bill_dict['other_expense']:.2f}"
        bill_dict['discount'] = f"{bill_dict['discount']:.2f}"
        bill_dict['gst_percentage'] = f"{bill_dict['gst_percentage']:.2f}"
        bill_dict['gst_amount'] = f"{bill_dict['gst_amount']:.2f}"
        bill_dict['cgst'] = f"{bill_dict['cgst']:.2f}"
        bill_dict['sgst'] = f"{bill_dict['sgst']:.2f}"
        bill_dict['grand_total'] = f"{bill_dict['grand_total']:.2f}"
        
        pdf_buffer = generate_dealer_bill_pdf(bill_dict)
        pdf_buffer.seek(0)
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'dealer_bill_{bill_id}.pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 400

