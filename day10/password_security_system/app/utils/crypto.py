import secrets
import hashlib
import hmac
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Optional
from jose import jwt, JWTError
import os

class CryptoTokenManager:
    def __init__(self):
        self.secret_key = os.getenv("SECRET_KEY", "fallback-secret-key")
        self.algorithm = os.getenv("JWT_ALGORITHM", "HS256")

    def generate_secure_token(self, payload: Dict, expire_minutes: int = 15) -> str:
        """Generate cryptographically secure token with embedded context"""
        # Add security metadata
        now = datetime.utcnow()
        payload.update({
            'iat': now,
            'exp': now + timedelta(minutes=expire_minutes),
            'nonce': secrets.token_hex(16),
            'type': payload.get('type', 'generic')
        })
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str, expected_type: str = None) -> Optional[Dict]:
        """Verify and decode token with type checking"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Verify token type if specified
            if expected_type and payload.get('type') != expected_type:
                return None
                
            return payload
            
        except JWTError:
            return None

    def generate_password_reset_token(self, user_id: str, email: str) -> str:
        """Generate secure password reset token"""
        payload = {
            'user_id': user_id,
            'email': email,
            'type': 'password_reset',
            'purpose': 'reset_password'
        }
        return self.generate_secure_token(payload, expire_minutes=15)

    def generate_email_verification_token(self, user_id: str, email: str) -> str:
        """Generate email verification token"""
        payload = {
            'user_id': user_id,
            'email': email,
            'type': 'email_verification',
            'purpose': 'verify_email'
        }
        return self.generate_secure_token(payload, expire_minutes=60)

    def create_hmac_signature(self, data: str, timestamp: str) -> str:
        """Create HMAC signature for data integrity"""
        message = f"{data}:{timestamp}"
        return hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

    def verify_hmac_signature(self, data: str, timestamp: str, signature: str) -> bool:
        """Verify HMAC signature"""
        expected = self.create_hmac_signature(data, timestamp)
        return hmac.compare_digest(expected, signature)
