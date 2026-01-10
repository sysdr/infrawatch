from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.models.user import User, UserStatus
from app.models.team import Team
from app.models.permission import Permission
from app.models.activity import Activity

router = APIRouter()

@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Get dashboard statistics"""
    
    # Get total users
    total_users_result = await db.execute(select(func.count(User.id)))
    total_users = total_users_result.scalar() or 0
    
    # Get active teams
    active_teams_result = await db.execute(select(func.count(Team.id)))
    active_teams = active_teams_result.scalar() or 0
    
    # Get total permissions
    total_permissions_result = await db.execute(select(func.count(Permission.id)))
    total_permissions = total_permissions_result.scalar() or 0
    
    # Get active users
    active_users_result = await db.execute(
        select(func.count(User.id)).where(
            User.status == UserStatus.ACTIVE,
            User.is_active == True
        )
    )
    active_users = active_users_result.scalar() or 0
    
    # Get recent activities count (last 24 hours)
    from datetime import datetime, timedelta
    since = datetime.utcnow() - timedelta(hours=24)
    recent_activities_result = await db.execute(
        select(func.count(Activity.id)).where(Activity.timestamp >= since)
    )
    recent_activities = recent_activities_result.scalar() or 0
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "active_teams": active_teams,
        "total_permissions": total_permissions,
        "recent_activities": recent_activities
    }

