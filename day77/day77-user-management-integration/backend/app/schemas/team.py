from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.team import TeamRole

class TeamBase(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None

class TeamCreate(TeamBase):
    pass

class TeamResponse(TeamBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class TeamMemberAdd(BaseModel):
    user_id: int
    role: TeamRole = TeamRole.MEMBER

class TeamMemberResponse(BaseModel):
    id: int
    team_id: int
    user_id: int
    role: TeamRole
    joined_at: datetime
    
    class Config:
        from_attributes = True
