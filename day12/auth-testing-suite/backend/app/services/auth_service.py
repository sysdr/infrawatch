from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime

from app.models.user import User
from app.schemas.auth import UserCreate, UserLogin, UserResponse, Token
from app.services.jwt_service import jwt_service

class AuthService:
    
    async def register_user(self, db: Session, user_data: UserCreate) -> Token:
        # Check if user exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists with this email"
            )
        
        # Create new user
        user = User(
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name
        )
        user.set_password(user_data.password)
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Generate tokens
        token_data = {"user_id": user.id, "email": user.email, "role": user.role}
        access_token = jwt_service.create_access_token(token_data)
        refresh_token = jwt_service.create_refresh_token(token_data)
        
        # Save refresh token
        user.add_refresh_token(refresh_token)
        db.commit()
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse.from_orm(user)
        )
    
    async def authenticate_user(self, db: Session, credentials: UserLogin) -> Token:
        user = db.query(User).filter(User.email == credentials.email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        if user.is_locked:
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account temporarily locked due to too many failed attempts"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )
        
        if not user.verify_password(credentials.password):
            user.increment_login_attempts()
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Reset login attempts on success
        user.reset_login_attempts()
        user.last_login = datetime.utcnow()
        
        # Generate tokens
        token_data = {"user_id": user.id, "email": user.email, "role": user.role}
        access_token = jwt_service.create_access_token(token_data)
        refresh_token = jwt_service.create_refresh_token(token_data)
        
        # Save refresh token
        user.add_refresh_token(refresh_token)
        db.commit()
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse.from_orm(user)
        )
    
    async def refresh_tokens(self, db: Session, refresh_token: str) -> Token:
        payload = jwt_service.verify_refresh_token(refresh_token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user = db.query(User).filter(User.id == payload["user_id"]).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Check if refresh token exists
        token_exists = any(
            t.get("token") == refresh_token 
            for t in (user.refresh_tokens or [])
        )
        if not token_exists:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token not found or expired"
            )
        
        # Generate new tokens
        token_data = {"user_id": user.id, "email": user.email, "role": user.role}
        new_access_token = jwt_service.create_access_token(token_data)
        new_refresh_token = jwt_service.create_refresh_token(token_data)
        
        # Replace old refresh token
        user.remove_refresh_token(refresh_token)
        user.add_refresh_token(new_refresh_token)
        db.commit()
        
        return Token(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            user=UserResponse.from_orm(user)
        )

auth_service = AuthService()
