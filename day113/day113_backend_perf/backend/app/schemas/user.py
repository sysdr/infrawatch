from pydantic import BaseModel
from typing import Optional
from datetime import datetime
class UserOut(BaseModel):
    id: str
    email: str
    name: str
    team_id: Optional[str] = None
    is_active: bool
    login_count: int
    created_at: Optional[datetime] = None
    model_config = {"from_attributes": True}
class TeamOut(BaseModel):
    id: str
    name: str
    created_at: Optional[datetime] = None
    model_config = {"from_attributes": True}
class PaginatedUsers(BaseModel):
    data: list[UserOut]
    next_cursor: Optional[str] = None
    total: int
    cached: bool = False
