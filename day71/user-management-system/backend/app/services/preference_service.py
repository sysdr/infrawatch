from sqlalchemy.orm import Session
from typing import Dict
from datetime import datetime
from ..models.preference import UserPreference, DEFAULT_PREFERENCES
from ..core.redis_client import redis_client
from .activity_service import activity_service

class PreferenceService:
    @staticmethod
    async def get_preferences(db: Session, user_id: int) -> Dict:
        try:
            # Try cache first (if Redis is available)
        cache_key = f"prefs:{user_id}"
            try:
        cached = await redis_client.get(cache_key)
        if cached:
            return cached
            except Exception:
                # Redis not available, continue without cache
                pass
        
            # Get from database
        pref_obj = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
        preferences = pref_obj.preferences if pref_obj else DEFAULT_PREFERENCES.copy()
        
            # Cache for 1 hour (if Redis is available)
            try:
        await redis_client.set(cache_key, preferences, expire=3600)
            except Exception:
                # Redis not available, continue without caching
                pass
        
        return preferences
        except Exception as e:
            # If anything fails, return default preferences
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error getting preferences for user {user_id}: {e}. Returning defaults.")
            return DEFAULT_PREFERENCES.copy()
    
    @staticmethod
    async def update_preferences(
        db: Session,
        user_id: int,
        new_prefs: Dict
    ) -> UserPreference:
        pref_obj = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
        
        if not pref_obj:
            pref_obj = UserPreference(
                user_id=user_id,
                preferences=DEFAULT_PREFERENCES.copy()
            )
            db.add(pref_obj)
        
        # Merge preferences (deep update)
        current = pref_obj.preferences
        current.update(new_prefs)
        pref_obj.preferences = current
        pref_obj.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(pref_obj)
        
        # Invalidate cache (if Redis is available)
        try:
        await redis_client.delete(f"prefs:{user_id}")
        except Exception:
            # Redis not available, continue without cache invalidation
            pass
        
        # Track activity (non-blocking)
        try:
        await activity_service.track_activity(
            db, user_id, "preference.updated",
            description="User preferences updated",
                activity_metadata={"updated_keys": list(new_prefs.keys())}
        )
        except Exception:
            # Activity tracking failed, but don't fail the update
            pass
        
        return pref_obj

preference_service = PreferenceService()
