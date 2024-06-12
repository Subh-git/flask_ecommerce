from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Order, OrderItem, Cart, Product, Payment, User
from app import db
from datetime import datetime

order_bp = Blueprint('order_bp', __name__)


current_transaction_id = 0

def generate_transaction_id():
    global current_transaction_id
    current_transaction_id += 1
    return current_transaction_id


@order_bp.route('/', methods=['POST'])
@jwt_required()
def create_order():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            current_app.logger.warning(f"User with id {current_user_id} not found")
            return jsonify({'message': 'User not found'}), 404

        cart_items = Cart.query.filter_by(user_id=user.id).all()

        if not cart_items:
            current_app.logger.warning(f"User {user.id} attempted to create an order with an empty cart")
            return jsonify({'message': 'Cart is empty'}), 400

        total_amount = 0
        order_items = []

        for item in cart_items:
            product = Product.query.get(item.product_id)
            if product.quantity < item.quantity:
                current_app.logger.warning(f"Not enough quantity for product {product.name}")
                return jsonify({'message': f'Not enough quantity for product {product.name}'}), 400
            product.quantity -= item.quantity

            item_total = product.price * item.quantity

            discount_config = current_app.config.get('DEFAULT_DISCOUNTS', {})
            for quantity, discount in discount_config.items():
                if item.quantity >= int(quantity):
                    item_total *= (1 - float(discount) / 100)

            total_amount += item_total
            order_items.append(OrderItem(product_id=product.id, quantity=item.quantity, price=item_total))

        order = Order(user_id=user.id, total_amount=total_amount, status='Pending')
        db.session.add(order)
        db.session.flush()

        for order_item in order_items:
            order_item.order_id = order.id
            db.session.add(order_item)

        db.session.commit()

        current_app.logger.info(f"Order {order.id} created successfully for user {user.id}")
        return jsonify({'message': 'Order created successfully', 'order_id': order.id}), 201

    except Exception as e:
        current_app.logger.error(f"Error creating order: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@order_bp.route('/payment', methods=['POST'])
@jwt_required()
def process_payment():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            current_app.logger.warning(f"User with id {current_user_id} not found")
            return jsonify({'message': 'User not found'}), 404

        data = request.get_json()
        order_id = data.get('order_id')
        payment_method = data.get('payment_method')

        order = Order.query.filter_by(id=order_id, user_id=user.id, status='Pending').first()

        if not order:
            current_app.logger.warning(f"Order {order_id} not found or already processed for user {user.id}")
            return jsonify({'message': 'Order not found or already processed'}), 404

        payment = Payment(
            order_id=order.id,
            amount=order.total_amount,
            payment_method=payment_method,
            status='Success',
            transaction_id = generate_transaction_id(),
            created_at= datetime.now()
        )
        order.status = 'Completed'
        db.session.add(payment)
        db.session.commit()

        current_app.logger.info(f"Payment processed successfully for order {order.id}")
        return jsonify({'message': 'Payment processed successfully'}), 200

    except Exception as e:
        current_app.logger.error(f"Error processing payment for order {order_id}: {e}")
        return jsonify({'message': 'Internal server error'}), 500

