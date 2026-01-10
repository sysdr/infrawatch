from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class PermissionBase(BaseModel):
    name: str
    resource: str
    action: str
    description: Optional[str] = None

class PermissionCreate(PermissionBase):
    pass

class PermissionResponse(PermissionBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

class PermissionAssign(BaseModel):
    permission_id: UUID

class PermissionCheckRequest(BaseModel):
    resource: str
    action: str

class PermissionCheckResponse(BaseModel):
    allowed: bool
    reason: Optional[str] = None
