from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class TeamBase(BaseModel):
    name: str
    description: Optional[str] = None
    parent_team_id: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = {}

class TeamCreate(TeamBase):
    organization_id: int

class TeamUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class TeamMemberAdd(BaseModel):
    user_id: int
    role_id: int

class TeamResponse(TeamBase):
    id: int
    organization_id: int
    slug: str
    materialized_path: str
    member_count: int
    last_activity_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

class TeamMemberResponse(BaseModel):
    id: int
    team_id: int
    user_id: int
    role_id: int
    joined_at: datetime
    effective_permissions: List[str]
    
    class Config:
        from_attributes = True

class TeamDashboardMetrics(BaseModel):
    team_id: int
    team_name: str
    total_members: int
    active_members_today: int
    active_members_week: int
    total_activities: int
    recent_activities: List[Dict[str, Any]]
    member_activity_distribution: Dict[str, int]

class OrganizationCreate(BaseModel):
    name: str
    slug: str
    settings: Optional[Dict[str, Any]] = {}

class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: List[str] = []
