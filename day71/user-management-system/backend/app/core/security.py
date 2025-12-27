from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import hashlib
import bcrypt
from .config import settings

# Use bcrypt directly to avoid passlib initialization issues
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _prehash_password(password: str) -> str:
    """
    Pre-hash password with SHA256 to handle bcrypt's 72-byte limit.
    This ensures passwords longer than 72 bytes are handled correctly.
    Returns the SHA256 hex digest (64 characters).
    """
    password_bytes = password.encode('utf-8')
    return hashlib.sha256(password_bytes).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    Always pre-hash with SHA256 first to match the hashing strategy.
    """
    # Always pre-hash to match the hashing strategy
    prehashed = _prehash_password(plain_password)
    # Use bcrypt directly instead of passlib
    try:
        return bcrypt.checkpw(prehashed.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    Always pre-hash with SHA256 first to avoid bcrypt's 72-byte limit.
    """
    # Always pre-hash to avoid bcrypt 72-byte limit
    prehashed = _prehash_password(password)
    # Use bcrypt directly instead of passlib to avoid initialization issues
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(prehashed.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
