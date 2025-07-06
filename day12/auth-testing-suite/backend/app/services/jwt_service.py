from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
import uuid

from app.core.config import settings

class JWTService:
    def __init__(self):
        self.access_secret = settings.JWT_SECRET_KEY
        self.refresh_secret = settings.JWT_REFRESH_SECRET_KEY
        self.access_expire = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        self.refresh_expire = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
    def create_access_token(self, data: Dict[str, Any]) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + self.access_expire
        to_encode.update({
            "exp": expire,
            "type": "access",
            "jti": str(uuid.uuid4()),
            "iat": datetime.utcnow(),
            "iss": "auth-api",
            "aud": "auth-client"
        })
        return jwt.encode(to_encode, self.access_secret, algorithm="HS256")
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + self.refresh_expire
        to_encode.update({
            "exp": expire,
            "type": "refresh",
            "jti": str(uuid.uuid4()),
            "iat": datetime.utcnow(),
            "iss": "auth-api",
            "aud": "auth-client"
        })
        return jwt.encode(to_encode, self.refresh_secret, algorithm="HS256")
    
    def verify_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            payload = jwt.decode(
                token, 
                self.access_secret, 
                algorithms=["HS256"],
                issuer="auth-api",
                audience="auth-client"
            )
            
            if payload.get("type") != "access":
                return None
                
            return payload
        except JWTError:
            return None
    
    def verify_refresh_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            payload = jwt.decode(
                token, 
                self.refresh_secret, 
                algorithms=["HS256"],
                issuer="auth-api",
                audience="auth-client"
            )
            
            if payload.get("type") != "refresh":
                return None
                
            return payload
        except JWTError:
            return None

jwt_service = JWTService()
