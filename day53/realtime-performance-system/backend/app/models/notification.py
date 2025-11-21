from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class NotificationBase(BaseModel):
    user_id: str
    message: str
    priority: str = "normal"  # critical, normal, low
    notification_type: str = "info"

class NotificationCreate(NotificationBase):
    pass

class Notification(NotificationBase):
    id: int
    created_at: datetime
    delivered: bool = False
    delivered_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class NotificationBatch(BaseModel):
    notifications: list[Notification]
    count: int
    timestamp: datetime

class ConnectionMetrics(BaseModel):
    active_connections: int
    memory_usage_mb: float
    messages_per_second: float
    average_latency_ms: float
    queue_depth: int
    timestamp: datetime
