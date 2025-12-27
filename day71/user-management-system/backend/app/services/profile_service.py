from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from ..models.profile import UserProfile
from ..schemas.profile import UserProfileUpdate
from ..core.redis_client import redis_client
from .activity_service import activity_service

class ProfileService:
    @staticmethod
    async def get_profile(db: Session, user_id: int) -> Optional[UserProfile]:
        # Try cache
        cached = await redis_client.get(f"profile:{user_id}")
        if cached:
            pass  # Would reconstruct profile
        
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        return profile
    
    @staticmethod
    async def update_profile(
        db: Session,
        user_id: int,
        profile_data: UserProfileUpdate
    ) -> UserProfile:
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            profile = UserProfile(user_id=user_id)
            db.add(profile)
        
        update_dict = profile_data.dict(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(profile, key, value)
        
        profile.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(profile)
        
        # Invalidate cache
        await redis_client.delete(f"profile:{user_id}")
        
        await activity_service.track_activity(
            db, user_id, "profile.updated",
            description="User profile updated"
        )
        
        return profile

profile_service = ProfileService()
