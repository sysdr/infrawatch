from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.user import UserStatus

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    status: Optional[UserStatus] = None

class UserResponse(UserBase):
    id: int
    status: UserStatus
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True
