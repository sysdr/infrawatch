from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ....core.database import get_db
from ....schemas.profile import UserProfileResponse, UserProfileUpdate
from ....services.profile_service import profile_service
from ....models.user import User
from ..deps.auth import get_current_active_user

router = APIRouter(prefix="/profile", tags=["profile"])

@router.get("/me", response_model=UserProfileResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    profile = await profile_service.get_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.put("/me", response_model=UserProfileResponse)
async def update_my_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    profile = await profile_service.update_profile(db, current_user.id, profile_data)
    return profile
