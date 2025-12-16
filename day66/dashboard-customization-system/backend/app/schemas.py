from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class WidgetConfig(BaseModel):
    widget_id: str
    widget_type: str
    position: List[int] = Field(..., min_length=4, max_length=4)
    config: Dict[str, Any] = {}

class DashboardConfig(BaseModel):
    layout: List[WidgetConfig]
    metadata: Optional[Dict[str, Any]] = {}

class DashboardCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    config: DashboardConfig
    theme: str = "light"
    is_template: bool = False

class DashboardUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    config: Optional[DashboardConfig] = None
    theme: Optional[str] = None
    version: int

class DashboardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    owner_id: UUID
    name: str
    description: Optional[str]
    config: Dict[str, Any]
    theme: str
    is_template: bool
    version: int
    created_at: datetime
    updated_at: datetime

class ShareCreate(BaseModel):
    permission: str = Field(..., pattern="^(view|edit|admin)$")
    expires_in_hours: Optional[int] = None

class ShareResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    dashboard_id: UUID
    share_token: str
    permission: str
    expires_at: Optional[datetime]
    created_at: datetime

class UserCreate(BaseModel):
    email: str
    username: str
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    email: str
    username: str
    theme_preference: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
