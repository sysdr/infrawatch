from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class AuditLogResponse(BaseModel):
    id: int
    log_id: str
    action_type: str
    actor: str
    resource_type: str
    resource_id: Optional[str]
    action_result: str
    ip_address: str
    user_agent: Optional[str]
    before_state: Optional[Dict[str, Any]]
    after_state: Optional[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]] = Field(alias="audit_metadata")
    created_at: datetime
    
    class Config:
        from_attributes = True
        populate_by_name = True

class AuditLogFilter(BaseModel):
    action_type: Optional[str] = None
    actor: Optional[str] = None
    resource_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    action_result: Optional[str] = None
