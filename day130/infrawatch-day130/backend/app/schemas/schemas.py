from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SubscriptionKeys(BaseModel):
    p256dh: str
    auth: str

class PushSubscriptionCreate(BaseModel):
    user_id: str
    endpoint: str
    keys: SubscriptionKeys
    user_agent: Optional[str] = None

class PushSubscriptionOut(BaseModel):
    id: str
    user_id: str
    endpoint: str
    is_active: bool
    created_at: datetime
    model_config = {"from_attributes": True}

class NotificationPreferenceUpdate(BaseModel):
    alerts_enabled: Optional[bool] = None
    team_updates_enabled: Optional[bool] = None
    daily_digest_enabled: Optional[bool] = None
    security_events_enabled: Optional[bool] = None
    quiet_hours_start: Optional[int] = None
    quiet_hours_end: Optional[int] = None
    quiet_hours_enabled: Optional[bool] = None

class NotificationPreferenceOut(BaseModel):
    user_id: str
    alerts_enabled: bool
    team_updates_enabled: bool
    daily_digest_enabled: bool
    security_events_enabled: bool
    quiet_hours_start: int
    quiet_hours_end: int
    quiet_hours_enabled: bool
    snoozed_until: Optional[datetime] = None
    model_config = {"from_attributes": True}

class NotificationEventCreate(BaseModel):
    notification_id: str
    event_type: str

class UserCreate(BaseModel):
    username: str
    email: str
    role: str = "engineer"
    timezone: str = "UTC"

class UserOut(BaseModel):
    id: str
    username: str
    email: str
    role: str
    timezone: str
    created_at: datetime
    model_config = {"from_attributes": True}

class SendNotificationRequest(BaseModel):
    user_id: str
    category: str
    title: str
    body: str
    url: str = "/"

class SnoozeRequest(BaseModel):
    user_id: str
    duration_minutes: int
