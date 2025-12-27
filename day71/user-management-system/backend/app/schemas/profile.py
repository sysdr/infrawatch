from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class UserProfileBase(BaseModel):
    display_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    timezone: Optional[str] = "UTC"
    job_title: Optional[str] = None
    department: Optional[str] = None
    company: Optional[str] = None

class UserProfileCreate(UserProfileBase):
    pass

class UserProfileUpdate(UserProfileBase):
    custom_fields: Optional[Dict] = None

class UserProfileResponse(UserProfileBase):
    id: int
    user_id: int
    custom_fields: Dict
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
