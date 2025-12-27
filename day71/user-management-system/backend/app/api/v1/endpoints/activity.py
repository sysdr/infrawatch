from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from ....core.database import get_db
from ....schemas.activity import UserActivityResponse, ActivityStats
from ....services.activity_service import activity_service
from ....models.user import User
from ..deps.auth import get_current_active_user

router = APIRouter(prefix="/activity", tags=["activity"])

@router.get("/me", response_model=List[UserActivityResponse])
async def get_my_activities(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    activities = await activity_service.get_user_activities(
        db, current_user.id, limit, offset
    )
    return activities

@router.get("/me/stats", response_model=ActivityStats)
async def get_my_activity_stats(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    stats = await activity_service.get_activity_stats(db, current_user.id, days)
    return stats
