from flask import Flask, request, jsonify, g, render_template
from flask_migrate import Migrate
from models.user import db, User
from auth.jwt_manager import JWTManager
from auth.decorators import jwt_required, admin_required
from config.config import config
import os
import redis

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Initialize JWT Manager with Redis
    redis_client = redis.from_url(app.config['REDIS_URL'])
    jwt_manager = JWTManager(app, redis_client)
    app.jwt_manager = jwt_manager  # Attach to app for global access
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    # Authentication routes
    @app.route('/auth/register', methods=['POST'])
    def register():
        data = request.get_json()
        
        # Validate input
        if not data or not all(k in data for k in ('email', 'password', 'first_name', 'last_name')):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if user exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create user
        user = User(
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=data.get('role', 'user')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'message': 'User created successfully', 'user': user.to_dict()}), 201
    
    @app.route('/auth/login', methods=['POST'])
    def login():
        data = request.get_json()
        
        if not data or not all(k in data for k in ('email', 'password')):
            return jsonify({'error': 'Email and password required'}), 400
        
        # Find user
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Generate tokens
        tokens = jwt_manager.generate_tokens(user.id, user.role)
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            **tokens
        }), 200
    
    @app.route('/auth/refresh', methods=['POST'])
    def refresh():
        data = request.get_json()
        refresh_token = data.get('refresh_token') if data else None
        
        if not refresh_token:
            return jsonify({'error': 'Refresh token required'}), 400
        
        # Generate new tokens
        new_tokens = jwt_manager.refresh_access_token(refresh_token)
        
        if not new_tokens:
            return jsonify({'error': 'Invalid or expired refresh token'}), 401
        
        return jsonify(new_tokens), 200
    
    @app.route('/auth/logout', methods=['POST'])
    @jwt_required
    def logout():
        # Get token from header
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1] if auth_header else None
        
        if token:
            jwt_manager.blacklist_token(token)
        
        return jsonify({'message': 'Logout successful'}), 200
    
    @app.route('/auth/profile', methods=['GET'])
    @jwt_required
    def profile():
        user = User.query.get(g.current_user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
    
    @app.route('/auth/admin-only', methods=['GET'])
    @jwt_required
    @admin_required
    def admin_only():
        return jsonify({'message': 'This is an admin-only endpoint', 'user_id': g.current_user_id}), 200
    
    # Health check
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'healthy', 'service': 'JWT Authentication Backend'}), 200
    
    # Main dashboard
    @app.route('/', methods=['GET'])
    def dashboard():
        return render_template('index.html')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
