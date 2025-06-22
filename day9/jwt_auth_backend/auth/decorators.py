from functools import wraps
from flask import request, jsonify, g, current_app

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
        
        # Validate token using the app's jwt_manager
        is_valid, payload, error = current_app.jwt_manager.validate_token(token)
        
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
