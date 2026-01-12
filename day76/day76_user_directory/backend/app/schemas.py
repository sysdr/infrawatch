from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEPROVISIONED = "deprovisioned"

class ProvisioningMethod(str, Enum):
    MANUAL = "manual"
    LDAP_SYNC = "ldap_sync"
    SSO_JIT = "sso_jit"
    SCIM = "scim"

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    department: Optional[str] = None
    employee_type: Optional[str] = None
    manager: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    department: Optional[str] = None
    employee_type: Optional[str] = None
    manager: Optional[str] = None
    status: Optional[UserStatus] = None

class UserResponse(UserBase):
    id: int
    status: UserStatus
    provisioning_method: ProvisioningMethod
    is_ldap_synced: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class LDAPConfigCreate(BaseModel):
    name: str
    server: str
    base_dn: str
    bind_dn: str
    bind_password: str
    user_filter: str = "(objectClass=inetOrgPerson)"
    sync_interval_minutes: int = 30

class LDAPConfigResponse(BaseModel):
    id: int
    name: str
    server: str
    base_dn: str
    sync_enabled: bool
    last_sync: Optional[datetime] = None
    is_active: bool
    
    class Config:
        from_attributes = True

class ImportRequest(BaseModel):
    users: List[UserCreate]
    update_existing: bool = False

class ImportStatus(BaseModel):
    job_id: int
    total_users: int
    processed: int
    created_count: int
    updated_count: int
    failed_count: int
    status: str
