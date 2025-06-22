#!/bin/bash

# JWT Authentication Backend Implementation Script
# Day 9: 180-Day Full Stack Development Series
# Creates a production-ready JWT authentication service

set -e  # Exit on any error

echo "🚀 Starting JWT Authentication Backend Implementation"
echo "Creating project structure and implementing JWT authentication service..."

# Project configuration
PROJECT_NAME="jwt_auth_backend"
PROJECT_DIR="$PWD/$PROJECT_NAME"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Step 1: Create project structure
print_status "Creating project structure..."
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

mkdir -p {auth,models,tests,config,utils}
mkdir -p tests/{unit,integration}

# Step 2: Create requirements.txt
print_status "Creating requirements.txt..."
cat > requirements.txt << 'EOF'
Flask==3.0.3
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.7
PyJWT==2.8.0
bcrypt==4.1.3
redis==5.0.4
python-dotenv==1.0.1
Werkzeug==3.0.2
marshmallow==3.21.1
pytest==8.2.0
pytest-flask==1.3.0
pytest-cov==5.0.0
requests==2.32.2
black==24.4.2
flake8==7.0.0
gunicorn==22.0.0
EOF

# Step 3: Create .env file
print_status "Creating environment configuration..."
cat > .env << 'EOF'
SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_SECRET_KEY=jwt-secret-key-for-token-signing
JWT_ACCESS_TOKEN_EXPIRES=900
JWT_REFRESH_TOKEN_EXPIRES=604800
DATABASE_URL=sqlite:///jwt_auth.db
REDIS_URL=redis://localhost:6379/0
FLASK_ENV=development
FLASK_DEBUG=True
EOF

# Step 4: Create config.py
print_status "Creating configuration module..."
cat > config/config.py << 'EOF'
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-dev-secret'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 900)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(seconds=int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES', 604800)))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///jwt_auth.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=60)

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
EOF

# Step 5: Create User model
print_status "Creating User model..."
cat > models/user.py << 'EOF'
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt
import uuid

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<User {self.email}>'
EOF

# Step 6: Create JWT Manager
print_status "Creating JWT Manager..."
cat > auth/jwt_manager.py << 'EOF'
import jwt
import redis
from datetime import datetime, timedelta
from flask import current_app
from typing import Dict, Optional, Tuple
import uuid

class JWTManager:
    def __init__(self, app=None, redis_client=None):
        self.app = app
        self.redis_client = redis_client
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        self.app = app
        if not self.redis_client:
            redis_url = app.config.get('REDIS_URL', 'redis://localhost:6379/0')
            self.redis_client = redis.from_url(redis_url)
    
    def generate_tokens(self, user_id: str, role: str = 'user') -> Dict[str, str]:
        """Generate access and refresh tokens"""
        now = datetime.utcnow()
        jti_access = str(uuid.uuid4())
        jti_refresh = str(uuid.uuid4())
        
        # Access token payload
        access_payload = {
            'user_id': user_id,
            'role': role,
            'type': 'access',
            'iat': now,
            'exp': now + current_app.config['JWT_ACCESS_TOKEN_EXPIRES'],
            'jti': jti_access
        }
        
        # Refresh token payload
        refresh_payload = {
            'user_id': user_id,
            'type': 'refresh',
            'iat': now,
            'exp': now + current_app.config['JWT_REFRESH_TOKEN_EXPIRES'],
            'jti': jti_refresh
        }
        
        # Generate tokens
        access_token = jwt.encode(
            access_payload,
            current_app.config['JWT_SECRET_KEY'],
            algorithm='HS256'
        )
        
        refresh_token = jwt.encode(
            refresh_payload,
            current_app.config['JWT_SECRET_KEY'],
            algorithm='HS256'
        )
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds()
        }
    
    def validate_token(self, token: str, token_type: str = 'access') -> Tuple[bool, Optional[Dict], Optional[str]]:
        """Validate JWT token"""
        try:
            # Check if token is blacklisted
            if self._is_token_blacklisted(token):
                return False, None, "Token has been revoked"
            
            # Decode token
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256'],
                options={"verify_exp": True}
            )
            
            # Verify token type
            if payload.get('type') != token_type:
                return False, None, f"Invalid token type. Expected {token_type}"
            
            return True, payload, None
            
        except jwt.ExpiredSignatureError:
            return False, None, "Token has expired"
        except jwt.InvalidTokenError as e:
            return False, None, f"Invalid token: {str(e)}"
    
    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """Generate new access token from refresh token"""
        is_valid, payload, error = self.validate_token(refresh_token, 'refresh')
        
        if not is_valid:
            return None
        
        # Generate new access token
        user_id = payload['user_id']
        # Note: In production, fetch role from database
        role = 'user'  # Simplified for demo
        
        new_tokens = self.generate_tokens(user_id, role)
        return new_tokens
    
    def blacklist_token(self, token: str) -> bool:
        """Add token to blacklist"""
        try:
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256'],
                options={"verify_exp": False}  # Don't verify expiration for blacklisting
            )
            
            jti = payload.get('jti')
            exp = payload.get('exp')
            
            if jti and exp:
                # Calculate TTL based on token expiration
                now = datetime.utcnow().timestamp()
                ttl = max(0, int(exp - now))
                
                # Store in Redis with TTL
                self.redis_client.setex(f"blacklist:{jti}", ttl, "1")
                return True
                
        except Exception as e:
            current_app.logger.error(f"Error blacklisting token: {e}")
        
        return False
    
    def _is_token_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted"""
        try:
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256'],
                options={"verify_exp": False}
            )
            
            jti = payload.get('jti')
            if jti:
                return self.redis_client.exists(f"blacklist:{jti}")
                
        except Exception:
            pass
        
        return False
EOF

# Step 7: Create Authentication Decorators
print_status "Creating authentication decorators..."
cat > auth/decorators.py << 'EOF'
from functools import wraps
from flask import request, jsonify, g
from auth.jwt_manager import JWTManager

jwt_manager = JWTManager()

def jwt_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        # Validate token
        is_valid, payload, error = jwt_manager.validate_token(token)
        
        if not is_valid:
            return jsonify({'error': error}), 401
        
        # Store user info in Flask's g object
        g.current_user_id = payload['user_id']
        g.current_user_role = payload.get('role', 'user')
        g.token_payload = payload
        
        return f(*args, **kwargs)
    
    return decorated_function

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'current_user_role') or g.current_user_role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    
    return decorated_function

def role_required(required_role):
    """Decorator to require specific role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'current_user_role') or g.current_user_role != required_role:
                return jsonify({'error': f'Role {required_role} required'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator
EOF

# Step 8: Create main application
print_status "Creating main Flask application..."
cat > app.py << 'EOF'
from flask import Flask, request, jsonify, g
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
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
EOF

# Step 9: Create comprehensive tests
print_status "Creating unit tests..."
cat > tests/test_jwt_auth.py << 'EOF'
import pytest
import json
from app import create_app, db
from models.user import User

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def sample_user(app):
    with app.app_context():
        user = User(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            role='user'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user

class TestAuthentication:
    def test_register_user(self, client):
        """Test user registration"""
        response = client.post('/auth/register', 
            json={
                'email': 'newuser@example.com',
                'password': 'password123',
                'first_name': 'New',
                'last_name': 'User'
            })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'User created successfully'
        assert data['user']['email'] == 'newuser@example.com'
    
    def test_register_duplicate_email(self, client, sample_user):
        """Test registration with existing email"""
        response = client.post('/auth/register',
            json={
                'email': 'test@example.com',
                'password': 'password123',
                'first_name': 'Another',
                'last_name': 'User'
            })
        
        assert response.status_code == 409
        data = json.loads(response.data)
        assert 'already registered' in data['error']
    
    def test_login_success(self, client, sample_user):
        """Test successful login"""
        response = client.post('/auth/login',
            json={
                'email': 'test@example.com',
                'password': 'password123'
            })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['user']['email'] == 'test@example.com'
    
    def test_login_invalid_credentials(self, client, sample_user):
        """Test login with invalid credentials"""
        response = client.post('/auth/login',
            json={
                'email': 'test@example.com',
                'password': 'wrongpassword'
            })
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'Invalid credentials' in data['error']
    
    def test_protected_endpoint_without_token(self, client):
        """Test accessing protected endpoint without token"""
        response = client.get('/auth/profile')
        assert response.status_code == 401
    
    def test_protected_endpoint_with_token(self, client, sample_user):
        """Test accessing protected endpoint with valid token"""
        # Login first
        login_response = client.post('/auth/login',
            json={
                'email': 'test@example.com',
                'password': 'password123'
            })
        
        token = json.loads(login_response.data)['access_token']
        
        # Access protected endpoint
        response = client.get('/auth/profile',
            headers={'Authorization': f'Bearer {token}'})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['user']['email'] == 'test@example.com'
    
    def test_token_refresh(self, client, sample_user):
        """Test token refresh functionality"""
        # Login first
        login_response = client.post('/auth/login',
            json={
                'email': 'test@example.com',
                'password': 'password123'
            })
        
        refresh_token = json.loads(login_response.data)['refresh_token']
        
        # Refresh token
        response = client.post('/auth/refresh',
            json={'refresh_token': refresh_token})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
        assert 'refresh_token' in data
    
    def test_logout(self, client, sample_user):
        """Test logout functionality"""
        # Login first
        login_response = client.post('/auth/login',
            json={
                'email': 'test@example.com',
                'password': 'password123'
            })
        
        token = json.loads(login_response.data)['access_token']
        
        # Logout
        response = client.post('/auth/logout',
            headers={'Authorization': f'Bearer {token}'})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Logout successful'
EOF

# Step 10: Create Docker configuration
print_status "Creating Docker configuration..."
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:create_app()"]
EOF

cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  jwt-auth:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - REDIS_URL=redis://redis:6379/0
      - DATABASE_URL=postgresql://jwt_user:jwt_password@postgres:5432/jwt_auth_db
    depends_on:
      - redis
      - postgres
    volumes:
      - .:/app
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: jwt_auth_db
      POSTGRES_USER: jwt_user
      POSTGRES_PASSWORD: jwt_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
EOF

# Step 11: Create demonstration script
print_status "Creating demonstration script..."
cat > demo.py << 'EOF'
#!/usr/bin/env python3
import requests
import json
import time
import sys

class JWTDemo:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.access_token = None
        self.refresh_token = None
    
    def print_response(self, response, description):
        print(f"\n{'='*50}")
        print(f"📋 {description}")
        print(f"{'='*50}")
        print(f"Status Code: {response.status_code}")
        try:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        except:
            print(f"Response: {response.text}")
    
    def test_health(self):
        """Test health endpoint"""
        response = requests.get(f"{self.base_url}/health")
        self.print_response(response, "Health Check")
        return response.status_code == 200
    
    def register_user(self):
        """Register a test user"""
        user_data = {
            "email": "demo@example.com",
            "password": "DemoPassword123!",
            "first_name": "Demo",
            "last_name": "User",
            "role": "user"
        }
        
        response = requests.post(f"{self.base_url}/auth/register", json=user_data)
        self.print_response(response, "User Registration")
        return response.status_code in [201, 409]  # 409 if user already exists
    
    def login_user(self):
        """Login with test user"""
        login_data = {
            "email": "demo@example.com",
            "password": "DemoPassword123!"
        }
        
        response = requests.post(f"{self.base_url}/auth/login", json=login_data)
        self.print_response(response, "User Login")
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data['access_token']
            self.refresh_token = data['refresh_token']
            return True
        return False
    
    def test_protected_endpoint(self):
        """Test accessing protected profile endpoint"""
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(f"{self.base_url}/auth/profile", headers=headers)
        self.print_response(response, "Protected Profile Endpoint")
        return response.status_code == 200
    
    def test_token_refresh(self):
        """Test token refresh functionality"""
        refresh_data = {"refresh_token": self.refresh_token}
        response = requests.post(f"{self.base_url}/auth/refresh", json=refresh_data)
        self.print_response(response, "Token Refresh")
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data['access_token']
            self.refresh_token = data['refresh_token']
            return True
        return False
    
    def test_logout(self):
        """Test logout functionality"""
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.post(f"{self.base_url}/auth/logout", headers=headers)
        self.print_response(response, "User Logout")
        return response.status_code == 200
    
    def test_access_after_logout(self):
        """Test accessing protected endpoint after logout"""
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(f"{self.base_url}/auth/profile", headers=headers)
        self.print_response(response, "Access After Logout (Should Fail)")
        return response.status_code == 401
    
    def run_full_demo(self):
        """Run complete demonstration"""
        print("🚀 Starting JWT Authentication Backend Demo")
        print("=" * 60)
        
        # Test sequence
        tests = [
            ("Health Check", self.test_health),
            ("User Registration", self.register_user),
            ("User Login", self.login_user),
            ("Protected Endpoint Access", self.test_protected_endpoint),
            ("Token Refresh", self.test_token_refresh),
            ("Updated Token Access", self.test_protected_endpoint),
            ("User Logout", self.test_logout),
            ("Access After Logout", self.test_access_after_logout)
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n🔍 Running: {test_name}")
            try:
                result = test_func()
                results.append((test_name, result))
                status = "✅ PASSED" if result else "❌ FAILED"
                print(f"Result: {status}")
            except Exception as e:
                print(f"❌ ERROR: {e}")
                results.append((test_name, False))
            
            time.sleep(1)  # Brief pause between tests
        
        # Summary
        print(f"\n{'='*60}")
        print("📊 DEMO SUMMARY")
        print(f"{'='*60}")
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name}: {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! JWT Authentication is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the output above for details.")
        
        return passed == total

if __name__ == "__main__":
    demo = JWTDemo()
    success = demo.run_full_demo()
    sys.exit(0 if success else 1)
EOF

chmod +x demo.py

# Step 12: Install dependencies and setup
print_status "Installing Python dependencies..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Step 13: Initialize database
print_status "Initializing database..."
export FLASK_APP=app.py
python3 -c "
from app import create_app, db
app = create_app('development')
with app.app_context():
    db.create_all()
    print('Database tables created successfully')
"

# Step 14: Run tests
print_status "Running unit tests..."
python3 -m pytest tests/ -v --tb=short

# Step 15: Start Redis (if not running)
print_status "Checking Redis availability..."
if ! redis-cli ping > /dev/null 2>&1; then
    print_warning "Redis not running. Starting Redis with Docker..."
    docker run -d --name jwt-redis -p 6379:6379 redis:7-alpine
    sleep 3
fi

# Step 16: Start application
print_status "Starting JWT Authentication Backend..."
python3 app.py &
APP_PID=$!

# Wait for application to start
sleep 5

# Step 17: Run demonstration
print_status "Running live demonstration..."
python3 demo.py

# Step 18: Test Docker build
print_status "Testing Docker build..."
docker build -t jwt-auth-backend .

# Step 19: Test with Docker Compose
print_status "Testing with Docker Compose..."
docker-compose up -d

# Wait for services to be ready
sleep 10

# Test with Docker environment
print_status "Testing Docker deployment..."
python3 demo.py

# Step 20: Cleanup
print_status "Cleaning up..."
kill $APP_PID 2>/dev/null || true
docker-compose down

print_success "JWT Authentication Backend implementation completed successfully!"
print_success "✅ Project structure created"
print_success "✅ Dependencies installed"
print_success "✅ Database initialized"
print_success "✅ Unit tests passed"
print_success "✅ Live demonstration completed"
print_success "✅ Docker build successful"
print_success "✅ Docker Compose deployment tested"

echo ""
echo "🎯 Implementation Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📁 Project: $PROJECT_DIR"
echo "🔑 Features: JWT generation, validation, refresh, blacklisting"
echo "🛡️  Security: bcrypt password hashing, token expiration, role-based access"
echo "📊 Testing: Comprehensive unit and integration tests"
echo "🐳 Docker: Production-ready containerization"
echo "🚀 Demo: Working authentication flow demonstration"
echo ""
echo "Next steps:"
echo "1. cd $PROJECT_DIR"
echo "2. source venv/bin/activate"
echo "3. python app.py (to start development server)"
echo "4. python demo.py (to run demonstration)"
echo "5. docker-compose up (for production deployment)"
echo ""
echo "🎉 Ready for Day 10: Password Security implementation!"