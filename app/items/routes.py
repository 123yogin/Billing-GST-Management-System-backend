from flask import Blueprint, request, jsonify
from app import db
from app.models import Item
import uuid

bp = Blueprint('items', __name__)

@bp.route('/items', methods=['POST'])
def create_item():
    """Create a new item (product)"""
    try:
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({'error': 'Name is required'}), 400
        
        # Handle price input (could be string, empty string, or number)
        price_input = data.get('price', 0)
        try:
            if isinstance(price_input, str) and price_input.strip() == '':
                price = 0
            else:
                price = float(price_input)
        except (ValueError, TypeError):
            price = 0

        product = Item(
            name=data['name'],
            hsn_code=data.get('hsn_code', ''),
            price=price
        )
        db.session.add(product)
        db.session.commit()
        
        return jsonify(product.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/items', methods=['GET'])
def get_items():
    """Get all items"""
    try:
        products = Item.query.order_by(Item.created_at.desc()).all()
        return jsonify([p.to_dict() for p in products]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/items/<item_id>', methods=['DELETE'])
def delete_item(item_id):
    """Delete an item"""
    try:
        product_uuid = uuid.UUID(item_id)
        product = Item.query.get_or_404(product_uuid)
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Item deleted successfully'}), 200
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid item ID format'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/items/<item_id>', methods=['PUT'])
def update_item(item_id):
    """Update an item"""
    try:
        product_uuid = uuid.UUID(item_id)
        product = Item.query.get_or_404(product_uuid)
        data = request.get_json()
        
        if 'name' in data:
            product.name = data['name']
        if 'hsn_code' in data:
            product.hsn_code = data['hsn_code']
        if 'price' in data:
            price_input = data['price']
            try:
                if isinstance(price_input, str) and price_input.strip() == '':
                    product.price = 0
                else:
                    product.price = float(price_input)
            except (ValueError, TypeError):
                pass # Keep existing price or set to 0? Let's just ignore invalid input for now or set 0.
            
        db.session.commit()
        return jsonify(product.to_dict()), 200
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid item ID format'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
