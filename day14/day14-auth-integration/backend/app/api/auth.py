from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import HTTPBearer
from app.models.user import UserLogin, UserCreate, UserResponse, Token, TokenRefresh, AuthResponse
from app.services.jwt_service import JWTService
from app.services.user_service import UserService
from app.core.config import settings
from datetime import timedelta

router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=AuthResponse)
async def register(user_data: UserCreate, response: Response):
    # Check if user exists
    existing_user = await UserService.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = await UserService.create_user(user_data)
    
    # Generate tokens
    access_token = JWTService.create_access_token({"sub": user.email, "user_id": user.id})
    refresh_token = JWTService.create_refresh_token({"sub": user.email, "user_id": user.id})
    
    # Set httpOnly cookie for refresh token
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    
    tokens = Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    
    return AuthResponse(user=user, tokens=tokens)

@router.post("/login", response_model=AuthResponse)
async def login(user_credentials: UserLogin, response: Response):
    user = await UserService.authenticate_user(user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Generate tokens
    access_token = JWTService.create_access_token({"sub": user.email, "user_id": user.id})
    refresh_token = JWTService.create_refresh_token({"sub": user.email, "user_id": user.id})
    
    # Set httpOnly cookie for refresh token
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    
    tokens = Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    
    return AuthResponse(user=user, tokens=tokens)

@router.post("/refresh", response_model=Token)
async def refresh_token(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found"
        )
    
    payload = JWTService.verify_token(refresh_token, "refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user = await UserService.get_user_by_email(payload.get("sub"))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Generate new tokens
    new_access_token = JWTService.create_access_token({"sub": user.email, "user_id": user.id})
    new_refresh_token = JWTService.create_refresh_token({"sub": user.email, "user_id": user.id})
    
    # Update httpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    
    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("refresh_token")
    return {"message": "Successfully logged out"}

@router.get("/verify")
async def verify_token(token: str = Depends(security)):
    payload = JWTService.verify_token(token.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    return {"valid": True, "payload": payload}
