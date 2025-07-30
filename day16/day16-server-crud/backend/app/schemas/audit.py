from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

class AuditLogResponse(BaseModel):
    id: int
    resource_type: str
    resource_id: str
    action: str
    user_id: str
    tenant_id: str
    changes: Dict[str, Any]
    audit_metadata: Dict[str, Any]
    timestamp: datetime
    ip_address: Optional[str]
    
    class Config:
        from_attributes = True
