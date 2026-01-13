from pydantic import BaseModel
from datetime import datetime
from app.models.permission import PermissionType

class PermissionBase(BaseModel):
    resource_type: str
    resource_id: str
    permission_type: PermissionType

class UserPermissionCreate(PermissionBase):
    user_id: int

class TeamPermissionCreate(PermissionBase):
    team_id: int

class PermissionResponse(PermissionBase):
    id: int
    granted_at: datetime
    
    class Config:
        from_attributes = True
