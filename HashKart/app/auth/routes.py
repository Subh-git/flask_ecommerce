from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User, db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            current_app.logger.warning("Signup failed: Missing username, email, or password")
            return jsonify({'message': 'Missing username, email, or password'}), 400

        if User.query.filter_by(username=username).first():
            current_app.logger.warning("Signup failed: Username already exists")
            return jsonify({'message': 'Username already exists'}), 400

        if User.query.filter_by(email=email).first():
            current_app.logger.warning("Signup failed: Email already exists")
            return jsonify({'message': 'Email already exists'}), 400

        user = User(username=username, email=email, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()

        current_app.logger.info(f"User {username} created successfully")
        return jsonify({'message': 'User created successfully'}), 201

    except Exception as e:
        current_app.logger.error(f"Error in signup: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password_hash, password):
            current_app.logger.warning("Login failed: Invalid username or password")
            return jsonify({'message': 'Invalid username or password'}), 401

        access_token = create_access_token(identity=user.id)
        current_app.logger.info(f"User {username} logged in successfully")
        return jsonify(access_token=access_token), 200

    except Exception as e:
        current_app.logger.error(f"Error in login: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            current_app.logger.warning(f"Profile access failed: User with id {current_user_id} not found")
            return jsonify({'message': 'User not found'}), 404

        current_app.logger.info(f"User {user.username} accessed their profile")
        return jsonify({'username': user.username, 'email': user.email}), 200

    except Exception as e:
        current_app.logger.error(f"Error in profile: {e}")
        return jsonify({'message': 'Internal server error'}), 500
