from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import List, Optional

from app.core.database import Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    role = Column(String, default="user")
    is_active = Column(Boolean, default=True)
    is_email_verified = Column(Boolean, default=False)
    last_login = Column(DateTime)
    login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)
    refresh_tokens = Column(JSON, default=list)
    permissions = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_user_email', 'email'),
        Index('idx_user_locked_until', 'locked_until'),
    )
    
    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.hashed_password)
    
    def set_password(self, password: str):
        self.hashed_password = pwd_context.hash(password)
    
    @property
    def is_locked(self) -> bool:
        return self.locked_until and self.locked_until > datetime.utcnow()
    
    def increment_login_attempts(self):
        if self.locked_until and self.locked_until < datetime.utcnow():
            self.login_attempts = 1
            self.locked_until = None
        else:
            self.login_attempts += 1
            
        if self.login_attempts >= 5:
            self.locked_until = datetime.utcnow() + timedelta(hours=2)
    
    def reset_login_attempts(self):
        self.login_attempts = 0
        self.locked_until = None
    
    def add_refresh_token(self, token: str):
        tokens = self.refresh_tokens or []
        tokens.append({"token": token, "created_at": datetime.utcnow().isoformat()})
        if len(tokens) > 5:
            tokens = tokens[-5:]
        self.refresh_tokens = tokens
    
    def remove_refresh_token(self, token: str):
        if self.refresh_tokens:
            self.refresh_tokens = [
                t for t in self.refresh_tokens if t.get("token") != token
            ]
