from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from services.service_container import notification_service
from models.notification import CreateNotificationRequest

router = APIRouter()

@router.get("/")
async def get_notifications(user_id: str = "demo-user", limit: int = 50):
    """Get notifications for a user"""
    try:
        notifications = await notification_service.get_notifications(user_id, limit)
        return {"notifications": notifications, "total": len(notifications)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_notification(request: CreateNotificationRequest):
    """Create a new notification"""
    try:
        notification = await notification_service.create_notification(request.dict())
        return {
            "id": notification.id,
            "title": notification.title,
            "message": notification.message,
            "type": notification.type.value,
            "priority": notification.priority.value,
            "timestamp": notification.timestamp.isoformat(),
            "userId": notification.userId
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{notification_id}/acknowledge")
async def acknowledge_notification(notification_id: str):
    """Acknowledge a notification"""
    try:
        await notification_service.acknowledge_notification(notification_id)
        return {"status": "acknowledged", "notificationId": notification_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
