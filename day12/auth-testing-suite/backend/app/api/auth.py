from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
import os
import logging

from app.core.database import get_db
from app.services.auth_service import auth_service
from app.schemas.auth import UserCreate, UserLogin, Token, TokenRefresh, Message, UserResponse
from app.dependencies import get_current_user
from app.core.config import settings
from app.models.user import User

router = APIRouter()

# Disable rate limiting in test mode
if settings.DEBUG or os.environ.get("DISABLE_RATE_LIMITING_FOR_TESTS") == "1":
    class DummyLimiter:
        def limit(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
    limiter = DummyLimiter()
else:
    limiter = Limiter(key_func=lambda request: request.client.host)

@router.post("/register", response_model=Token)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        # Log the incoming request data
        print(f"=== REGISTRATION REQUEST ===")
        print(f"Raw user_data: {user_data}")
        print(f"user_data.dict(): {user_data.dict()}")
        print(f"Email: {user_data.email}")
        print(f"First name: {user_data.first_name}")
        print(f"Last name: {user_data.last_name}")
        print(f"Password length: {len(user_data.password) if user_data.password else 0}")
        print(f"===========================")
        
        result = await auth_service.register_user(db, user_data)
        return result
    except HTTPException as e:
        print(f"HTTPException in register: {e.status_code} - {e.detail}")
        raise
    except Exception as e:
        print(f"Unexpected error in register: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )

@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
async def login(
    request: Request,
    credentials: UserLogin, 
    db: Session = Depends(get_db)
):
    return await auth_service.authenticate_user(db, credentials)

@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
):
    return await auth_service.refresh_tokens(db, token_data.refresh_token)

@router.post("/logout", response_model=Message)
async def logout(
    token_data: TokenRefresh,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Remove refresh token
    user = db.query(User).filter(User.id == current_user.id).first()
    if user:
        user.remove_refresh_token(token_data.refresh_token)
        db.commit()
    
    return Message(message="Logout successful")

@router.post("/logout-all", response_model=Message)
async def logout_all(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Clear all refresh tokens
    user = db.query(User).filter(User.id == current_user.id).first()
    if user:
        user.refresh_tokens = []
        db.commit()
    
    return Message(message="Logged out from all devices")

@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: UserResponse = Depends(get_current_user)):
    return current_user
