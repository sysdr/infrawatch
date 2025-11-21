from fastapi import APIRouter, HTTPException
from ..models.notification import NotificationCreate, Notification
from ..services.notification_service import notification_service

router = APIRouter()

@router.post("/", response_model=Notification)
async def create_notification(notification: NotificationCreate):
    """Create a new notification"""
    try:
        return await notification_service.create_notification(notification)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bulk")
async def create_bulk_notifications(notifications: list[NotificationCreate]):
    """Create multiple notifications"""
    try:
        results = []
        for notif in notifications:
            result = await notification_service.create_notification(notif)
            results.append(result)
        return {"created": len(results), "notifications": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
