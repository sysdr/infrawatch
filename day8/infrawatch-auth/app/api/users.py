from flask import Blueprint, request, jsonify
from app import db
from app.models.user import User
from app.utils.validators import validate_email, validate_password, validate_name

users_bp = Blueprint('users', __name__)

@users_bp.route('/users', methods=['POST'])
def create_user():
    """Create a new user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'User with this email already exists'}), 409
        
        # Validate password
        is_valid_password, password_errors = validate_password(password)
        if not is_valid_password:
            return jsonify({'error': 'Password validation failed', 'details': password_errors}), 400
        
        # Validate optional fields
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        
        if first_name and not validate_name(first_name):
            return jsonify({'error': 'Invalid first name format'}), 400
        
        if last_name and not validate_name(last_name):
            return jsonify({'error': 'Invalid last name format'}), 400
        
        # Create user
        user = User(
            email=email,
            password=password,
            first_name=first_name if first_name else None,
            last_name=last_name if last_name else None
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User created successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@users_bp.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get user by ID"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': user.to_dict()}), 200

@users_bp.route('/users', methods=['GET'])
def list_users():
    """List all users with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Limit per_page to prevent abuse
        per_page = min(per_page, 100)
        
        users = User.query.filter_by(is_active=True).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'users': [user.to_dict() for user in users.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': users.total,
                'pages': users.pages,
                'has_next': users.has_next,
                'has_prev': users.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@users_bp.route('/users/verify-password', methods=['POST'])
def verify_password():
    """Verify user password"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        user = User.query.filter_by(email=email, is_active=True).first()
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if user.check_password(password):
            user.update_login()
            return jsonify({
                'message': 'Password verified successfully',
                'user_id': user.id
            }), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500
