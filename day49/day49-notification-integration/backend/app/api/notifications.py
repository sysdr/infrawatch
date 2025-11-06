from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.models import Notification
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/")
async def list_notifications(
    user_id: Optional[str] = None,
    alert_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """List notifications with filters"""
    try:
        query = select(Notification).order_by(Notification.created_at.desc())
        
        if user_id:
            query = query.where(Notification.user_id == user_id)
        if alert_id:
            query = query.where(Notification.alert_id == alert_id)
        
        result = await db.execute(query)
        notifications = result.scalars().all()
        
        return [
            {
                "id": n.id,
                "alert_id": n.alert_id,
                "user_id": n.user_id,
                "channel": n.channel.value if hasattr(n.channel, 'value') else str(n.channel),
                "status": n.status.value if hasattr(n.status, 'value') else str(n.status),
                "message": n.message,
                "sent_at": n.sent_at.isoformat() if n.sent_at else None,
                "retry_count": n.retry_count,
                "failed_reason": n.failed_reason
            }
            for n in notifications
        ]
    except Exception as e:
        logger.error(f"Error listing notifications: {e}", exc_info=True)
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Failed to list notifications: {str(e)}")

@router.get("/stats")
async def notification_stats(db: AsyncSession = Depends(get_db)):
    """Get notification statistics"""
    try:
        result = await db.execute(select(Notification))
        notifications = result.scalars().all()
        
        total = len(notifications)
        by_status = {}
        by_channel = {}
        
        for n in notifications:
            # SQLAlchemy returns enum objects, access .value to get string
            status_val = n.status.value if n.status else 'UNKNOWN'
            channel_val = n.channel.value if n.channel else 'UNKNOWN'
            
            by_status[status_val] = by_status.get(status_val, 0) + 1
            by_channel[channel_val] = by_channel.get(channel_val, 0) + 1
        
        return {
            "total": total,
            "by_status": by_status,
            "by_channel": by_channel
        }
    except Exception as e:
        logger.error(f"Error getting notification stats: {str(e)}", exc_info=True)
        # Return empty stats on error
        return {
            "total": 0,
            "by_status": {},
            "by_channel": {}
        }
