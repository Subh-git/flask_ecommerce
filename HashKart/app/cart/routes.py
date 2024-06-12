from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Cart, Product, db

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/', methods=['GET'])
@jwt_required()
def get_cart():
    try:
        current_user_id = get_jwt_identity()
        cart_items = Cart.query.filter_by(user_id=current_user_id).all()
        current_app.logger.info(f"User {current_user_id} fetched cart items")
        return jsonify([{
            'product_id': item.product_id,
            'quantity': item.quantity
        } for item in cart_items]), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching cart items for user {current_user_id}: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@cart_bp.route('/', methods=['POST'])
@jwt_required()
def add_to_cart():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity')

        product = Product.query.get_or_404(product_id)
        if product.quantity < quantity:
            current_app.logger.warning(f"User {current_user_id} attempted to add more product {product_id} than available")
            return jsonify({'message': 'Not enough product quantity available'}), 400

        cart_item = Cart.query.filter_by(user_id=current_user_id, product_id=product_id).first()
        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = Cart(user_id=current_user_id, product_id=product_id, quantity=quantity)
            db.session.add(cart_item)

        db.session.commit()
        current_app.logger.info(f"User {current_user_id} added product {product_id} to cart")
        return jsonify({'message': 'Item added to cart successfully'}), 201

    except Exception as e:
        current_app.logger.error(f"Error adding item to cart for user {current_user_id}: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@cart_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(product_id):
    try:
        current_user_id = get_jwt_identity()
        cart_item = Cart.query.filter_by(user_id=current_user_id, product_id=product_id).first_or_404()
        db.session.delete(cart_item)
        db.session.commit()
        current_app.logger.info(f"User {current_user_id} removed product {product_id} from cart")
        return jsonify({'message': 'Item removed from cart successfully'}), 200

    except Exception as e:
        current_app.logger.error(f"Error removing item from cart for user {current_user_id}: {e}")
        return jsonify({'message': 'Internal server error'}), 500
