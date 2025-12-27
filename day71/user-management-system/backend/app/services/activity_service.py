from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from ..models.activity import UserActivity
from ..schemas.activity import UserActivityResponse, ActivityStats

class ActivityService:
    @staticmethod
    async def track_activity(
        db: Session,
        user_id: int,
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        description: Optional[str] = None,
        activity_metadata: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> UserActivity:
        activity = UserActivity(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            activity_metadata=activity_metadata or {},
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(activity)
        db.commit()
        db.refresh(activity)
        return activity
    
    @staticmethod
    async def get_user_activities(
        db: Session,
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[UserActivity]:
        return db.query(UserActivity)\
            .filter(UserActivity.user_id == user_id)\
            .order_by(desc(UserActivity.created_at))\
            .offset(offset)\
            .limit(limit)\
            .all()
    
    @staticmethod
    async def get_activity_stats(
        db: Session,
        user_id: int,
        days: int = 30
    ) -> ActivityStats:
        since = datetime.utcnow() - timedelta(days=days)
        
        # Total activities
        total = db.query(func.count(UserActivity.id))\
            .filter(UserActivity.user_id == user_id)\
            .filter(UserActivity.created_at >= since)\
            .scalar()
        
        # Activities by type
        by_type = db.query(
            UserActivity.action,
            func.count(UserActivity.id).label('count')
        ).filter(UserActivity.user_id == user_id)\
         .filter(UserActivity.created_at >= since)\
         .group_by(UserActivity.action)\
         .all()
        
        activities_by_type = {action: count for action, count in by_type}
        
        # Recent activities
        recent = db.query(UserActivity)\
            .filter(UserActivity.user_id == user_id)\
            .order_by(desc(UserActivity.created_at))\
            .limit(10)\
            .all()
        
        # Timeline (activities per day)
        timeline = db.query(
            func.date(UserActivity.created_at).label('date'),
            func.count(UserActivity.id).label('count')
        ).filter(UserActivity.user_id == user_id)\
         .filter(UserActivity.created_at >= since)\
         .group_by(func.date(UserActivity.created_at))\
         .order_by(func.date(UserActivity.created_at))\
         .all()
        
        activity_timeline = [
            {"date": str(date), "count": count}
            for date, count in timeline
        ]
        
        return ActivityStats(
            total_activities=total,
            activities_by_type=activities_by_type,
            recent_activities=recent,
            activity_timeline=activity_timeline
        )

activity_service = ActivityService()
