from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict
from ....core.database import get_db
from ....schemas.preference import UserPreferenceUpdate, UserPreferenceResponse
from ....services.preference_service import preference_service
from ....models.user import User
from ..deps.auth import get_current_active_user

router = APIRouter(prefix="/preferences", tags=["preferences"])

@router.get("/me", response_model=Dict)
async def get_my_preferences(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    try:
    preferences = await preference_service.get_preferences(db, current_user.id)
        # Ensure we always return a valid dict
        if not preferences or not isinstance(preferences, dict):
            from ....models.preference import DEFAULT_PREFERENCES
            preferences = DEFAULT_PREFERENCES.copy()
    return preferences
    except Exception as e:
        # If anything fails, return default preferences
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error getting preferences for user {current_user.id}: {e}")
        from ....models.preference import DEFAULT_PREFERENCES
        return DEFAULT_PREFERENCES.copy()

@router.put("/me", response_model=UserPreferenceResponse)
async def update_my_preferences(
    pref_data: UserPreferenceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    pref_obj = await preference_service.update_preferences(
        db, current_user.id, pref_data.preferences
    )
    return pref_obj
