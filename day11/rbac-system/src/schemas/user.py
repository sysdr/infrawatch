from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class PermissionBase(BaseModel):
    name: str
    description: Optional[str] = None
    resource: str
    action: str

class PermissionCreate(PermissionBase):
    pass

class Permission(PermissionBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    permission_ids: List[int] = []

class Role(RoleBase):
    id: int
    is_active: bool
    created_at: datetime
    permissions: List[Permission] = []
    
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str
    role_ids: List[int] = []

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = None
    role_ids: Optional[List[int]] = None

class User(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    roles: List[Role] = []
    
    class Config:
        from_attributes = True

class UserWithPermissions(User):
    permissions: List[str] = []

class RoleAssignment(BaseModel):
    user_id: int
    role_ids: List[int]
