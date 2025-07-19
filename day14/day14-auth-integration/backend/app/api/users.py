from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from app.models.user import UserResponse
from app.services.jwt_service import JWTService
from app.services.user_service import UserService

router = APIRouter()
security = HTTPBearer()

async def get_current_user(token: str = Depends(security)) -> UserResponse:
    payload = JWTService.verify_token(token.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user = await UserService.get_user_by_email(payload.get("sub"))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: UserResponse = Depends(get_current_user)):
    return current_user

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(current_user: UserResponse = Depends(get_current_user)):
    return current_user
