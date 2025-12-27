from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ....core.database import get_db
from ....schemas.user import UserResponse, UserUpdate
from ....services.user_service import user_service
from ....models.user import User
from ..deps.auth import get_current_active_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    try:
        updated_user = await user_service.update_user(db, current_user.id, user_data)
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
