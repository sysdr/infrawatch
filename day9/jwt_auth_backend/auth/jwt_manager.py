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
