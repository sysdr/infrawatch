from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.models import UserPreference
from app.core.redis_client import redis_client
from pydantic import BaseModel
from typing import Dict

router = APIRouter()

class PreferenceUpdate(BaseModel):
    email: str
    phone: str = None
    slack_id: str = None
    preferences: Dict = {}

@router.post("/{user_id}")
async def update_preferences(
    user_id: str,
    pref_data: PreferenceUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update user preferences"""
    try:
        result = await db.execute(select(UserPreference).where(UserPreference.user_id == user_id))
        pref = result.scalar_one_or_none()
        
        if pref:
            pref.email = pref_data.email
            pref.phone = pref_data.phone
            pref.slack_id = pref_data.slack_id
            pref.preferences = pref_data.preferences
        else:
            pref = UserPreference(
                user_id=user_id,
                email=pref_data.email,
                phone=pref_data.phone,
                slack_id=pref_data.slack_id,
                preferences=pref_data.preferences
            )
            db.add(pref)
        
        await db.commit()
        
        # Invalidate cache (don't fail if Redis is unavailable)
        try:
            if redis_client.redis is None:
                await redis_client.connect()
            await redis_client.set_preference_cache(user_id, pref_data.preferences)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Could not update Redis cache: {e}")
        
        return {"message": "Preferences updated"}
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error updating preferences for {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update preferences: {str(e)}")

@router.get("/{user_id}")
async def get_preferences(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get user preferences"""
    try:
        result = await db.execute(select(UserPreference).where(UserPreference.user_id == user_id))
        pref = result.scalar_one_or_none()
        
        if not pref:
            raise HTTPException(status_code=404, detail="User preferences not found")
        
        # Ensure preferences is a dict (JSON field)
        prefs_dict = pref.preferences if isinstance(pref.preferences, dict) else {}
        
        return {
            "user_id": pref.user_id,
            "email": pref.email or "",
            "phone": pref.phone or "",
            "slack_id": pref.slack_id or "",
            "preferences": prefs_dict
        }
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error getting preferences for {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get preferences: {str(e)}")
