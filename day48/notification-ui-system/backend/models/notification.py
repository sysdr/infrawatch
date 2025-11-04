from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

class NotificationType(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

class NotificationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class NotificationChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"

class Notification(BaseModel):
    id: str
    title: str
    message: str
    type: NotificationType
    priority: NotificationPriority
    timestamp: datetime
    userId: str
    acknowledged: bool = False
    data: Optional[Dict[str, Any]] = None

class NotificationPreference(BaseModel):
    id: str
    userId: str
    channel: NotificationChannel
    enabled: bool
    types: List[NotificationType]
    priorities: List[NotificationPriority]
    settings: Optional[Dict[str, Any]] = None

class NotificationHistory(BaseModel):
    id: str
    notificationId: str
    action: str  # sent, acknowledged, failed
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None

class CreateNotificationRequest(BaseModel):
    title: str
    message: str
    type: NotificationType
    priority: NotificationPriority
    userId: str
    data: Optional[Dict[str, Any]] = None

class UpdatePreferenceRequest(BaseModel):
    channel: Optional[NotificationChannel] = None
    enabled: Optional[bool] = None
    types: Optional[List[NotificationType]] = None
    priorities: Optional[List[NotificationPriority]] = None
    settings: Optional[Dict[str, Any]] = None
