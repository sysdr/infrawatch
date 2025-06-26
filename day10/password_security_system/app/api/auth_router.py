from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from fastapi.security import HTTPBearer
from slowapi import Limiter
from slowapi.util import get_remote_address
import redis.asyncio as redis
from datetime import datetime
import secrets
import json
from pydantic import BaseModel

from app.models.user import *
from app.security.password_validator import PasswordStrengthValidator
from app.security.lockout_manager import AccountLockoutManager
from app.security.rate_limiter import TokenBucketRateLimiter
from app.utils.crypto import CryptoTokenManager

router = APIRouter()
security = HTTPBearer()

# Initialize components
password_validator = PasswordStrengthValidator()
crypto_manager = CryptoTokenManager()

class PasswordCheckRequest(BaseModel):
    password: str

async def get_redis(request: Request) -> redis.Redis:
    """Dependency to get Redis client from app state"""
    return request.app.state.redis

@router.post("/check-password-strength")
async def check_password_strength(data: PasswordCheckRequest):
    """Check password strength and provide detailed feedback"""
    result = password_validator.validate_strength(data.password)
    return PasswordStrengthResponse(**result)

@router.post("/register")
async def register_user(
    user_data: UserCreate,
    request: Request,
    background_tasks: BackgroundTasks,
    redis_client: redis.Redis = Depends(get_redis)
):
    """Register new user with email verification"""
    
    if not redis_client:
        raise HTTPException(status_code=500, detail="Database connection not available")
    
    # Rate limiting
    rate_limiter = TokenBucketRateLimiter(redis_client)
    client_ip = get_remote_address(request)
    rate_check = await rate_limiter.is_allowed(f"register:{client_ip}", 3, 300)  # 3 per 5 min
    
    if not rate_check['allowed']:
        raise HTTPException(
            status_code=429,
            detail=f"Too many registration attempts. Try again in {rate_check['retry_after']} seconds"
        )
    
    # Validate password strength
    strength_check = password_validator.validate_strength(user_data.password)
    if not strength_check['valid']:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Password does not meet security requirements",
                "violations": strength_check['violations'],
                "suggestions": strength_check['suggestions']
            }
        )
    
    # Check if user already exists
    user_key = f"user:{user_data.email}"
    existing_user = await redis_client.get(user_key)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create user
    user_id = secrets.token_urlsafe(16)
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    user = User(
        id=user_id,
        email=user_data.email,
        hashed_password=pwd_context.hash(user_data.password),
        created_at=datetime.now(),
        is_verified=False
    )
    
    # Store user
    await redis_client.setex(user_key, 86400 * 30, user.json())  # 30 days
    
    # Generate email verification token
    verification_token = crypto_manager.generate_email_verification_token(user_id, user_data.email)
    
    # Store verification token
    token_key = f"verify_token:{verification_token}"
    await redis_client.setex(token_key, 3600, user_id)  # 1 hour
    
    return {
        "message": "User registered successfully",
        "user_id": user_id,
        "verification_token": verification_token,  # In production, send via email
        "verification_required": True
    }

@router.post("/verify-email")
async def verify_email(
    verification: EmailVerification,
    request: Request,
    redis_client: redis.Redis = Depends(get_redis)
):
    """Verify user email address"""
    
    if not redis_client:
        raise HTTPException(status_code=500, detail="Database connection not available")
    
    # Verify token
    token_payload = crypto_manager.verify_token(verification.token, 'email_verification')
    if not token_payload:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")
    
    # Get user
    user_key = f"user:{token_payload['email']}"
    user_data = await redis_client.get(user_key)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update user verification status
    user = User.parse_raw(user_data)
    user.is_verified = True
    
    await redis_client.setex(user_key, 86400 * 30, user.json())
    
    # Clean up verification token
    token_key = f"verify_token:{verification.token}"
    await redis_client.delete(token_key)
    
    return {"message": "Email verified successfully"}

@router.post("/login")
async def login_user(
    login_data: UserLogin,
    request: Request,
    redis_client: redis.Redis = Depends(get_redis)
):
    """Authenticate user with advanced security measures"""
    
    if not redis_client:
        raise HTTPException(status_code=500, detail="Database connection not available")
    
    client_ip = get_remote_address(request)
    identifier = f"{login_data.email}:{client_ip}"
    
    # Rate limiting
    rate_limiter = TokenBucketRateLimiter(redis_client)
    rate_check = await rate_limiter.is_allowed(f"login:{client_ip}", 10, 300)  # 10 per 5 min
    
    if not rate_check['allowed']:
        raise HTTPException(
            status_code=429,
            detail=f"Too many login attempts. Try again in {rate_check['retry_after']} seconds"
        )
    
    # Account lockout check
    lockout_manager = AccountLockoutManager(redis_client)
    if await lockout_manager.is_locked_out(identifier):
        lockout_status = await lockout_manager.get_lockout_status(identifier)
        raise HTTPException(
            status_code=423,
            detail={
                "message": "Account temporarily locked due to too many failed attempts",
                "unlock_time": lockout_status.get('unlock_time'),
                "attempts": lockout_status['attempts']
            }
        )
    
    # Get user
    user_key = f"user:{login_data.email}"
    user_data = await redis_client.get(user_key)
    if not user_data:
        # Record failed attempt even for non-existent users
        await lockout_manager.record_failed_attempt(identifier)
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user = User.parse_raw(user_data)
    
    # Verify password
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    if not pwd_context.verify(login_data.password, user.hashed_password):
        lockout_result = await lockout_manager.record_failed_attempt(identifier)
        
        detail = "Invalid credentials"
        if lockout_result['locked_out']:
            detail = {
                "message": "Too many failed attempts. Account locked.",
                "unlock_time": lockout_result['unlock_time'],
                "attempts": lockout_result['attempts']
            }
        
        raise HTTPException(status_code=401, detail=detail)
    
    # Check if email is verified
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")
    
    # Successful login
    await lockout_manager.record_successful_attempt(identifier)
    
    # Update last login
    user.last_login = datetime.now()
    await redis_client.setex(user_key, 86400 * 30, user.json())
    
    # Generate JWT token
    from jose import jwt
    import os
    
    token_payload = {
        "user_id": user.id,
        "email": user.email,
        "exp": datetime.utcnow().timestamp() + 1800  # 30 minutes
    }
    
    access_token = jwt.encode(
        token_payload,
        os.getenv("SECRET_KEY", "fallback-secret"),
        algorithm="HS256"
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
        "expires_in": 1800
    }

@router.post("/request-password-reset")
async def request_password_reset(
    reset_request: PasswordResetRequest,
    request: Request,
    redis_client: redis.Redis = Depends(get_redis)
):
    """Request password reset with secure token generation"""
    
    if not redis_client:
        raise HTTPException(status_code=500, detail="Database connection not available")
    
    client_ip = get_remote_address(request)
    
    # Rate limiting for password reset requests
    rate_limiter = TokenBucketRateLimiter(redis_client)
    rate_check = await rate_limiter.is_allowed(f"reset:{client_ip}", 3, 3600)  # 3 per hour
    
    if not rate_check['allowed']:
        raise HTTPException(
            status_code=429,
            detail=f"Too many reset requests. Try again in {rate_check['retry_after']} seconds"
        )
    
    # Check if user exists (but don't reveal if they don't)
    user_key = f"user:{reset_request.email}"
    user_data = await redis_client.get(user_key)
    
    if user_data:
        user = User.parse_raw(user_data)
        
        # Generate reset token
        reset_token = crypto_manager.generate_password_reset_token(user.id, user.email)
        
        # Store reset token
        token_key = f"reset_token:{reset_token}"
        await redis_client.setex(token_key, 900, user.id)  # 15 minutes
        
        return {
            "message": "Password reset token generated",
            "reset_token": reset_token  # In production, send via email only
        }
    
    # Always return success to prevent user enumeration
    return {"message": "If the email exists, a reset link has been sent"}

@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordReset,
    request: Request,
    redis_client: redis.Redis = Depends(get_redis)
):
    """Reset password using secure token"""
    
    if not redis_client:
        raise HTTPException(status_code=500, detail="Database connection not available")
    
    # Verify reset token
    token_payload = crypto_manager.verify_token(reset_data.token, 'password_reset')
    if not token_payload:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    # Validate new password strength
    strength_check = password_validator.validate_strength(reset_data.new_password)
    if not strength_check['valid']:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "New password does not meet security requirements",
                "violations": strength_check['violations'],
                "suggestions": strength_check['suggestions']
            }
        )
    
    # Get user
    user_key = f"user:{token_payload['email']}"
    user_data = await redis_client.get(user_key)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update password
    user = User.parse_raw(user_data)
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    user.hashed_password = pwd_context.hash(reset_data.new_password)
    await redis_client.setex(user_key, 86400 * 30, user.json())
    
    # Invalidate reset token
    token_key = f"reset_token:{reset_data.token}"
    await redis_client.delete(token_key)
    
    # Clear any existing lockouts for this user
    lockout_manager = AccountLockoutManager(redis_client)
    await lockout_manager.record_successful_attempt(f"{user.email}:*")
    
    return {"message": "Password reset successfully"}
