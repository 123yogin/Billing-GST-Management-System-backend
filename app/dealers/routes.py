from flask import Blueprint, request, jsonify
from app import db
from app.models import Dealer
import uuid
from sqlalchemy import text

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
        dealer_uuid = uuid.UUID(dealer_id)
        dealer = Dealer.query.get_or_404(dealer_uuid)
        return jsonify(dealer.to_dict()), 200
    except (ValueError, TypeError) as e:
        return jsonify({'error': 'Invalid dealer ID format'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@bp.route('/dealers/<dealer_id>', methods=['PUT'])
def update_dealer(dealer_id):
    """Update a dealer"""
    try:
        dealer_uuid = uuid.UUID(dealer_id)
        dealer = Dealer.query.get_or_404(dealer_uuid)
        data = request.get_json()
        
        if 'name' in data:
            dealer.name = data['name']
        if 'phone' in data:
            dealer.phone = data['phone']
        if 'address' in data:
            dealer.address = data['address']
        if 'gstin' in data:
            dealer.gstin = data['gstin']
        
        db.session.commit()
        return jsonify(dealer.to_dict()), 200
    except (ValueError, TypeError) as e:
        return jsonify({'error': 'Invalid dealer ID format'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/dealers/<dealer_id>', methods=['DELETE'])
def delete_dealer(dealer_id):
    """Delete a dealer"""
    try:
        dealer_uuid = uuid.UUID(dealer_id)
        dealer = Dealer.query.get_or_404(dealer_uuid)
        db.session.delete(dealer)
        db.session.commit()
        return jsonify({'message': 'Dealer deleted successfully'}), 200
    except (ValueError, TypeError) as e:
        return jsonify({'error': 'Invalid dealer ID format'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
