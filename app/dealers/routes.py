from flask import Blueprint, request, jsonify
from app import db
from app.models import Dealer
import uuid

bp = Blueprint('dealers', __name__)

@bp.route('/dealers', methods=['POST'])
def create_dealer():
    """Create a new dealer"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({'error': 'Name is required'}), 400
        
        # Create dealer
        dealer = Dealer(
            name=data['name'],
            phone=data.get('phone', ''),
            address=data.get('address', ''),
            khata_no=data.get('khata_no', ''),
            gstin=data.get('gstin', '')
        )
        db.session.add(dealer)
        db.session.commit()
        
        return jsonify(dealer.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/dealers', methods=['GET'])
def get_dealers():
    """Get all dealers"""
    try:
        dealers = Dealer.query.order_by(Dealer.created_at.desc()).all()
        return jsonify([dealer.to_dict() for dealer in dealers]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/dealers/<dealer_id>', methods=['GET'])
def get_dealer(dealer_id):
    """Get a specific dealer by ID"""
    try:
        dealer = Dealer.query.get_or_404(dealer_id)
        return jsonify(dealer.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@bp.route('/dealers/<dealer_id>', methods=['PUT'])
def update_dealer(dealer_id):
    """Update a dealer"""
    try:
        dealer = Dealer.query.get_or_404(dealer_id)
        data = request.get_json()
        
        if 'name' in data:
            dealer.name = data['name']
        if 'phone' in data:
            dealer.phone = data['phone']
        if 'address' in data:
            dealer.address = data['address']
        if 'khata_no' in data:
            dealer.khata_no = data['khata_no']
        if 'gstin' in data:
            dealer.gstin = data['gstin']
        
        db.session.commit()
        return jsonify(dealer.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/dealers/<dealer_id>', methods=['DELETE'])
def delete_dealer(dealer_id):
    """Delete a dealer"""
    try:
        dealer = Dealer.query.get_or_404(dealer_id)
        db.session.delete(dealer)
        db.session.commit()
        return jsonify({'message': 'Dealer deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
