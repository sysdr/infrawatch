from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class NotificationRequest(BaseModel):
    channel: str
    priority: str
    message: str
    recipient: Optional[str] = None

@router.post("/send")
async def send_notification(request: NotificationRequest):
    """Send a notification"""
    from app.main import integration_hub
    
    if not integration_hub:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    result = await integration_hub.notification_engine.send_notification({
        "channel": request.channel,
        "priority": request.priority,
        "message": request.message,
        "recipient": request.recipient
    })
    
    return result
