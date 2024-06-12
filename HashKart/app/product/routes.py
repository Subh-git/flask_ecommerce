from flask import Blueprint, request, jsonify, current_app
from app.models import Product
from app import db
from flask_jwt_extended import jwt_required, get_jwt_identity

product_bp = Blueprint('product_bp', __name__)

@product_bp.route('/', methods=['GET'])
@jwt_required()
def get_products():
    try:
        sort_by = request.args.get('sort_by')
        category = request.args.get('category')
        min_price = request.args.get('min_price')
        max_price = request.args.get('max_price')
        min_rating = request.args.get('min_rating')
        max_rating = request.args.get('max_rating')

        query = Product.query

        if category:
            query = query.filter_by(category=category)
        if min_price:
            query = query.filter(Product.price >= float(min_price))
        if max_price:
            query = query.filter(Product.price <= float(max_price))
        if min_rating:
            query = query.filter(Product.rating >= float(min_rating))
        if max_rating:
            query = query.filter(Product.rating <= float(max_rating))

        if sort_by:
            if sort_by == 'price':
                query = query.order_by(Product.price)
            elif sort_by == 'rating':
                query = query.order_by(Product.rating)

        products = query.all()

        return jsonify([{
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'quantity': product.quantity,
            'category': product.category,
            'rating': product.rating
        } for product in products]), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_products: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@product_bp.route('/', methods=['POST'])
@jwt_required()
def add_product():
    try:
        data = request.get_json()
        new_product = Product(
            name=data['name'],
            description=data['description'],
            price=data['price'],
            quantity=data['quantity'],
            category=data['category'],
            rating=data['rating']
        )
        db.session.add(new_product)
        db.session.commit()
        current_app.logger.info("Product added successfully")
        return jsonify({'message': 'Product added successfully'}), 201
    except Exception as e:
        current_app.logger.error(f"Error in add_product: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@product_bp.route('/<int:product_id>', methods=['GET'])
@jwt_required()
def get_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        return jsonify({
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'quantity': product.quantity,
            'category': product.category,
            'rating': product.rating
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_product: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@product_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    try:
        current_user_id = get_jwt_identity()
        product = Product.query.get(product_id)
        if product:
            db.session.delete(product)
            db.session.commit()
            current_app.logger.info("Product deleted successfully")
            return jsonify({'message': 'Product deleted successfully'}), 200
        else:
            current_app.logger.warning("Product not found")
            return jsonify({'message': 'Product not found'}), 404
    except Exception as e:
        current_app.logger.error(f"Error in delete_product: {e}")
        return jsonify({'message': 'Internal server error'}), 500
