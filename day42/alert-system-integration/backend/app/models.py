from enum import Enum
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field

class AlertState(str, Enum):
    OK = "ok"
    PENDING = "pending"
    FIRING = "firing"
    RESOLVED = "resolved"

class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    RETRYING = "retrying"

class AlertRule(BaseModel):
    id: str
    name: str
    metric: str
    condition: str  # >, <, >=, <=, ==
    threshold: float
    duration: int  # seconds
    severity: AlertSeverity
    enabled: bool = True
    labels: Dict[str, str] = Field(default_factory=dict)

class Alert(BaseModel):
    id: str
    rule_id: str
    rule_name: str
    state: AlertState
    severity: AlertSeverity
    current_value: float
    threshold: float
    started_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    labels: Dict[str, str] = Field(default_factory=dict)
    message: str

class Notification(BaseModel):
    id: str
    alert_id: str
    channel: str
    status: NotificationStatus
    attempts: int = 0
    max_attempts: int = 3
    created_at: datetime
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None

class MetricData(BaseModel):
    metric: str
    value: float
    timestamp: datetime
    labels: Dict[str, str] = Field(default_factory=dict)

class WebSocketMessage(BaseModel):
    type: str
    data: Dict
    timestamp: datetime
