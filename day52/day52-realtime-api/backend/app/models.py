from pydantic import BaseModel, Field
from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

class EventType(str, Enum):
    NOTIFICATION_CREATED = "notification.created"
    NOTIFICATION_READ = "notification.read"
    USER_UPDATED = "user.updated"
    MESSAGE_SENT = "message.sent"
    STATUS_CHANGED = "status.changed"
    SYSTEM_ALERT = "system.alert"

class Event(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: EventType
    payload: Dict[str, Any]
    client_id: str
    version: int = 0
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ConnectionMetrics(BaseModel):
    client_id: str
    connected_at: datetime
    last_activity: datetime
    events_sent: int = 0
    events_received: int = 0
