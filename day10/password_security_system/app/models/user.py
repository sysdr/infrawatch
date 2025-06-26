from datetime import datetime
from typing import Optional, Dict, List
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    id: str
    email: EmailStr
    hashed_password: str
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime
    last_login: Optional[datetime] = None
    failed_attempts: int = 0
    locked_until: Optional[datetime] = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class PasswordReset(BaseModel):
    token: str
    new_password: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class EmailVerification(BaseModel):
    token: str

class PasswordStrengthResponse(BaseModel):
    valid: bool
    strength: str
    score: float
    entropy: float
    requirements: Dict[str, bool]
    violations: List[str]
    suggestions: List[str]
    crack_time: Dict[str, str]
