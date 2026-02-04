from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class Alert(BaseModel):
    id: str
    alert_type: str
    severity: str
    title: str
    description: str
    context: Dict[str, Any]
    triggered_at: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    detection_latency_ms: Optional[float] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "alert-12345",
                "alert_type": "credential_stuffing",
                "severity": "HIGH",
                "title": "Credential Stuffing Detected",
                "description": "Multiple failed login attempts from different IPs",
                "context": {
                    "user_id": "testuser",
                    "attempt_count": 10,
                    "unique_ips": ["1.2.3.4", "5.6.7.8"]
                },
                "triggered_at": "2025-02-03T10:30:00Z",
                "resolved": False
            }
        }
