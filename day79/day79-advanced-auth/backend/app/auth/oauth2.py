import secrets
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

class OAuth2Service:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        # Generate RSA key pair for JWT signing
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
    
    @staticmethod
    def generate_code_verifier() -> str:
        """Generate code verifier for PKCE"""
        return secrets.token_urlsafe(64)
    
    @staticmethod
    def generate_code_challenge(verifier: str) -> str:
        """Generate code challenge from verifier"""
        digest = hashlib.sha256(verifier.encode()).digest()
        return base64.urlsafe_b64encode(digest).rstrip(b'=').decode()
    
    @staticmethod
    def verify_code_challenge(verifier: str, challenge: str) -> bool:
        """Verify code challenge matches verifier"""
        computed = OAuth2Service.generate_code_challenge(verifier)
        return secrets.compare_digest(computed, challenge)
    
    @staticmethod
    def generate_authorization_code() -> str:
        """Generate authorization code"""
        return secrets.token_urlsafe(32)
    
    def create_access_token(self, user_id: str, scopes: List[str], expires_delta: timedelta) -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + expires_delta
        to_encode = {
            "sub": user_id,
            "scopes": scopes,
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(16)
        }
        
        private_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        return jwt.encode(to_encode, private_pem, algorithm="RS256")
    
    def create_refresh_token(self, user_id: str) -> str:
        """Create refresh token"""
        return secrets.token_urlsafe(64)
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token"""
        try:
            public_pem = self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            payload = jwt.decode(token, public_pem, algorithms=["RS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
