from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class SecurityEventCreate(BaseModel):
    event_type: str
    severity: str
    source: str
    destination: Optional[str] = None
    user_id: Optional[str] = None
    ip_address: str
    user_agent: Optional[str] = None
    description: str
    metadata: Optional[Dict[str, Any]] = None
    threat_score: int = 0

class SecurityEventResponse(BaseModel):
    id: int
    event_id: str
    event_type: str
    severity: str
    source: str
    destination: Optional[str]
    user_id: Optional[str]
    ip_address: str
    user_agent: Optional[str]
    description: str
    metadata: Optional[Dict[str, Any]] = Field(alias="event_metadata")
    threat_score: int
    is_resolved: bool
    resolved_by: Optional[str]
    resolved_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True
        populate_by_name = True

class SecurityEventFilter(BaseModel):
    event_type: Optional[str] = None
    severity: Optional[str] = None
    user_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_resolved: Optional[bool] = None
    min_threat_score: Optional[int] = None
