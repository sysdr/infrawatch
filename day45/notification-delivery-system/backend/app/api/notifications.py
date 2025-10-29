from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

router = APIRouter()

class NotificationRequest(BaseModel):
    user_id: int
    channel: str  # email, sms, push
    priority: str = "normal"  # low, normal, high, urgent
    recipient: str
    subject: Optional[str] = None
    content: str
    template_id: Optional[str] = None
    template_data: Optional[Dict[str, Any]] = None
    scheduled_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class NotificationResponse(BaseModel):
    notification_id: str
    status: str
    message: str
    tracking_id: str

# In-memory storage for demo (use database in production)
notifications_store: Dict[str, Dict[str, Any]] = {}

@router.post("/send", response_model=NotificationResponse)
async def send_notification(request: NotificationRequest):
    """Send a new notification"""
    try:
        notification_id = str(uuid.uuid4())
        tracking_id = f"track_{notification_id[:8]}"
        
        notification_data = {
            "id": notification_id,
            "tracking_id": tracking_id,
            "user_id": request.user_id,
            "channel": request.channel,
            "priority": request.priority,
            "recipient": request.recipient,
            "subject": request.subject,
            "content": request.content,
            "template_id": request.template_id,
            "template_data": request.template_data,
            "scheduled_at": request.scheduled_at or datetime.now(),
            "metadata": request.metadata or {},
            "status": "queued",
            "created_at": datetime.now(),
            "retry_count": 0
        }
        
        # Store notification
        notifications_store[notification_id] = notification_data
        
        # TODO: Add to queue manager
        
        return NotificationResponse(
            notification_id=notification_id,
            status="queued",
            message="Notification queued for delivery",
            tracking_id=tracking_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue notification: {str(e)}")

@router.get("/bulk-send")
async def send_bulk_notifications():
    """Send multiple demo notifications for testing"""
    demo_notifications = [
        {
            "user_id": 1,
            "channel": "email",
            "priority": "high",
            "recipient": "user1@example.com",
            "subject": "Welcome!",
            "content": "Welcome to our platform!"
        },
        {
            "user_id": 2,
            "channel": "sms",
            "priority": "normal",
            "recipient": "+1234567890",
            "content": "Your order has been shipped!"
        },
        {
            "user_id": 3,
            "channel": "push",
            "priority": "urgent",
            "recipient": "device_token_123",
            "content": "Security alert: New login detected"
        }
    ]
    
    results = []
    for notif_data in demo_notifications:
        request = NotificationRequest(**notif_data)
        result = await send_notification(request)
        results.append(result)
    
    return {"message": f"Sent {len(results)} notifications", "notifications": results}

@router.get("/{notification_id}")
async def get_notification(notification_id: str):
    """Get notification details"""
    if notification_id not in notifications_store:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return notifications_store[notification_id]

@router.get("/")
async def list_notifications(skip: int = 0, limit: int = 100):
    """List notifications"""
    notifications = list(notifications_store.values())
    return {
        "notifications": notifications[skip:skip+limit],
        "total": len(notifications)
    }
