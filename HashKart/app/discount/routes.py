from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Discount, Order, db, User
from datetime import datetime

discount_bp = Blueprint('discount', __name__)

@discount_bp.route('/add', methods=['POST'])
def add_discount():
    try:
        data = request.get_json()
        code = data.get('code')
        description = data.get('description')
        discount_percent = data.get('discount_percent')
        valid_from = datetime.strptime(data.get('valid_from'), "%d-%m-%Y")
        valid_to = datetime.strptime(data.get('valid_to'), "%d-%m-%Y")

        new_discount = Discount(
            code=code,
            description=description,
            discount_percent=discount_percent,
            valid_from=valid_from,
            valid_to=valid_to
        )

        db.session.add(new_discount)
        db.session.commit()

        current_app.logger.info(f"New discount {code} added successfully")
        return jsonify({'message': 'Discount added successfully'}), 201

    except Exception as e:
        current_app.logger.error(f"Error adding discount: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@discount_bp.route('/', methods=['GET'])
def get_discounts():
    try:
        discounts = Discount.query.all()
        current_app.logger.info("Fetched all discounts")
        return jsonify([{
            'id': discount.id,
            'code': discount.code,
            'description': discount.description,
            'discount_percent': discount.discount_percent,
            'valid_from': discount.valid_from,
            'valid_to': discount.valid_to
        } for discount in discounts]), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching discounts: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@discount_bp.route('/apply', methods=['POST'])
@jwt_required()
def apply_discount():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            current_app.logger.warning(f"User with id {current_user_id} not found")
            return jsonify({'message': 'User not found'}), 404

        data = request.get_json()
        code = data.get('code')
        order_id = data.get('order_id')

        discount = Discount.query.filter_by(code=code).first()
        if not discount or discount.valid_from > datetime.now() or discount.valid_to < datetime.now():
            current_app.logger.warning(f"Invalid or expired discount code: {code}")
            return jsonify({'message': 'Invalid or expired discount code'}), 400

        order = Order.query.get_or_404(order_id)
        if order.status != 'Pending':
            current_app.logger.warning(f"Order {order_id} is not pending")
            return jsonify({'message': 'Order is not pending'}), 400

        discount_amount = order.total_amount * (discount.discount_percent / 100)
        order.total_amount -= discount_amount

        db.session.commit()

        current_app.logger.info(f"Discount {code} applied to order {order_id}")
        return jsonify({'message': 'Discount applied successfully', 'new_total': order.total_amount}), 200

    except Exception as e:
        current_app.logger.error(f"Error applying discount: {e}")
        return jsonify({'message': 'Internal server error'}), 500
