from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import timedelta
import logging
from ....core.database import get_db
from ....core.config import settings
from ....core.security import create_access_token
from ....schemas.user import UserCreate, UserLogin, Token, UserResponse
from ....services.user_service import user_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        logger.info(f"Attempting to register user with email: {user_data.email}")
        user = await user_service.create_user(db, user_data)
        logger.info(f"User registered successfully: {user.id}")
        # Ensure user is refreshed and all relationships are loaded
        db.refresh(user)
        return user
    except ValueError as e:
        error_msg = str(e) if str(e) else "Registration failed"
        logger.warning(f"Registration validation error: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    except SQLAlchemyError as e:
        error_msg = str(e)
        logger.error(f"Database error during registration: {error_msg}", exc_info=True)
        db.rollback()
        # Check if it's a connection error
        if "connection" in error_msg.lower() or "refused" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database service unavailable. Please ensure PostgreSQL is running."
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred. Please try again later."
        )
    except Exception as e:
        error_msg = str(e)
        error_type = type(e).__name__
        logger.error(f"Unexpected registration error ({error_type}): {error_msg}", exc_info=True)
        # If it's a database-related error that wasn't caught, return appropriate message
        if "database" in error_msg.lower() or "connection" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database service unavailable. Please ensure PostgreSQL is running."
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during registration: {error_msg}"
        )

@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    ip_address = request.client.host if request.client else None
    
    try:
        user = await user_service.authenticate_user(
            db, credentials.email, credentials.password, ip_address
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_access_token(
        data={"sub": str(user.id), "type": "refresh"},
        expires_delta=refresh_token_expires
    )
    
    return Token(access_token=access_token, refresh_token=refresh_token)
