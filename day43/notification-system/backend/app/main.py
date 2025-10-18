from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from models.notification import NotificationChannel, NotificationPriority, NotificationStatus
from app.services.notification_service import NotificationService
import logging
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Notification System API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple notification class for API use
class Notification:
    def __init__(self, id: int, title: str, message: str, channel: NotificationChannel, 
                 recipient: str, priority: NotificationPriority, status: NotificationStatus,
                 created_at: datetime, extra_data: Optional[str] = None):
        self.id = id
        self.title = title
        self.message = message
        self.channel = channel
        self.recipient = recipient
        self.priority = priority
        self.status = status
        self.created_at = created_at
        self.extra_data = extra_data
        self.retry_count = 0
        self.delivered_at = None
        self.error_message = None

# Initialize services
notification_service = NotificationService()

# In-memory storage for demo (use database in production)
notifications_db = {}
stats_db = {
    "total_sent": 0,
    "total_delivered": 0,
    "total_failed": 0,
    "channels": {}
}

# Pydantic models
class NotificationCreate(BaseModel):
    title: str
    message: str
    channel: NotificationChannel
    recipient: str
    priority: NotificationPriority = NotificationPriority.MEDIUM
    metadata: Optional[Dict[str, Any]] = None

class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    channel: str
    recipient: str
    priority: str
    status: str
    retry_count: int
    created_at: datetime
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None

class BulkNotificationCreate(BaseModel):
    notifications: List[NotificationCreate]

class ChannelTest(BaseModel):
    channel: NotificationChannel
    recipient: str
    test_message: str = "This is a test notification"

@app.get("/")
async def root():
    return {"message": "Notification System API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/notifications", response_model=NotificationResponse)
async def create_notification(
    notification_data: NotificationCreate,
    background_tasks: BackgroundTasks
):
    """Create and send a notification"""
    
    # Create notification object
    notification_id = len(notifications_db) + 1
    notification = Notification(
        id=notification_id,
        title=notification_data.title,
        message=notification_data.message,
        channel=notification_data.channel,
        recipient=notification_data.recipient,
        priority=notification_data.priority,
        status=NotificationStatus.PENDING,
        created_at=datetime.utcnow(),
        extra_data=str(notification_data.metadata) if notification_data.metadata else None
    )
    
    # Validate notification
    errors = notification_service.validate_notification(notification)
    if errors:
        raise HTTPException(status_code=400, detail={"errors": errors})
    
    # Store notification
    notifications_db[notification_id] = notification
    
    # Send notification in background
    background_tasks.add_task(send_notification_task, notification)
    
    # Update stats
    stats_db["total_sent"] += 1
    
    return NotificationResponse(
        id=notification.id,
        title=notification.title,
        message=notification.message,
        channel=notification.channel.value,
        recipient=notification.recipient,
        priority=notification.priority.value,
        status=notification.status.value,
        retry_count=notification.retry_count,
        created_at=notification.created_at,
        delivered_at=notification.delivered_at,
        error_message=notification.error_message
    )

@app.post("/notifications/bulk")
async def create_bulk_notifications(
    bulk_data: BulkNotificationCreate,
    background_tasks: BackgroundTasks
):
    """Create and send multiple notifications"""
    
    notifications = []
    for notif_data in bulk_data.notifications:
        notification_id = len(notifications_db) + 1
        notification = Notification(
            id=notification_id,
            title=notif_data.title,
            message=notif_data.message,
            channel=notif_data.channel,
            recipient=notif_data.recipient,
            priority=notif_data.priority,
            status=NotificationStatus.PENDING,
            created_at=datetime.utcnow(),
            extra_data=str(notif_data.metadata) if notif_data.metadata else None
        )
        
        # Validate each notification
        errors = notification_service.validate_notification(notification)
        if errors:
            raise HTTPException(
                status_code=400, 
                detail={"notification_index": len(notifications), "errors": errors}
            )
        
        notifications_db[notification_id] = notification
        notifications.append(notification)
    
    # Send all notifications in background
    background_tasks.add_task(send_bulk_notifications_task, notifications)
    
    # Update stats
    stats_db["total_sent"] += len(notifications)
    
    return {
        "message": f"Queued {len(notifications)} notifications for delivery",
        "notification_ids": [n.id for n in notifications]
    }

@app.get("/notifications", response_model=List[NotificationResponse])
async def get_notifications(skip: int = 0, limit: int = 100):
    """Get all notifications with pagination"""
    notifications = list(notifications_db.values())[skip:skip + limit]
    return [
        NotificationResponse(
            id=n.id,
            title=n.title,
            message=n.message,
            channel=n.channel.value,
            recipient=n.recipient,
            priority=n.priority.value,
            status=n.status.value,
            retry_count=n.retry_count,
            created_at=n.created_at,
            delivered_at=n.delivered_at,
            error_message=n.error_message
        ) for n in notifications
    ]

@app.get("/notifications/{notification_id}", response_model=NotificationResponse)
async def get_notification(notification_id: int):
    """Get a specific notification"""
    notification = notifications_db.get(notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return NotificationResponse(
        id=notification.id,
        title=notification.title,
        message=notification.message,
        channel=notification.channel.value,
        recipient=notification.recipient,
        priority=notification.priority.value,
        status=notification.status.value,
        retry_count=notification.retry_count,
        created_at=notification.created_at,
        delivered_at=notification.delivered_at,
        error_message=notification.error_message
    )

@app.post("/channels/test")
async def test_channel(test_data: ChannelTest):
    """Test a specific notification channel"""
    
    # Create test notification
    notification = Notification(
        id=999999,  # Special test ID
        title="Test Notification",
        message=test_data.test_message,
        channel=test_data.channel,
        recipient=test_data.recipient,
        priority=NotificationPriority.MEDIUM,
        status=NotificationStatus.PENDING,
        created_at=datetime.utcnow()
    )
    
    # Validate
    errors = notification_service.validate_notification(notification)
    if errors:
        raise HTTPException(status_code=400, detail={"errors": errors})
    
    # Send test
    result = await notification_service.send_notification(notification)
    
    return {
        "channel": test_data.channel.value,
        "recipient": test_data.recipient,
        "result": result,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/channels/status")
async def get_channel_status():
    """Get status of all notification channels"""
    return await notification_service.get_channel_stats()

@app.get("/stats")
async def get_stats():
    """Get notification statistics"""
    channel_stats = {}
    for notification in notifications_db.values():
        channel = notification.channel.value
        if channel not in channel_stats:
            channel_stats[channel] = {"sent": 0, "delivered": 0, "failed": 0}
        
        channel_stats[channel]["sent"] += 1
        if notification.status == NotificationStatus.DELIVERED:
            channel_stats[channel]["delivered"] += 1
        elif notification.status == NotificationStatus.FAILED:
            channel_stats[channel]["failed"] += 1
    
    return {
        "total_notifications": len(notifications_db),
        "total_delivered": len([n for n in notifications_db.values() if n.status == NotificationStatus.DELIVERED]),
        "total_failed": len([n for n in notifications_db.values() if n.status == NotificationStatus.FAILED]),
        "channels": channel_stats,
        "uptime": "100%",  # Demo value
        "last_updated": datetime.utcnow().isoformat()
    }

# Background tasks
async def send_notification_task(notification: Notification):
    """Background task to send notification"""
    try:
        result = await notification_service.send_notification(notification)
        if result.get("success"):
            stats_db["total_delivered"] += 1
        else:
            stats_db["total_failed"] += 1
    except Exception as e:
        logger.error(f"Background task error: {str(e)}")
        stats_db["total_failed"] += 1

async def send_bulk_notifications_task(notifications: List[Notification]):
    """Background task to send bulk notifications"""
    try:
        results = await notification_service.send_bulk_notifications(notifications)
        delivered = len([r for r in results if r.get("success")])
        failed = len(results) - delivered
        
        stats_db["total_delivered"] += delivered
        stats_db["total_failed"] += failed
    except Exception as e:
        logger.error(f"Bulk background task error: {str(e)}")
        stats_db["total_failed"] += len(notifications)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
