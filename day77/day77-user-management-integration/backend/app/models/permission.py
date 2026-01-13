from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base

class PermissionType(str, enum.Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"

class UserPermission(Base):
    __tablename__ = "user_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resource_type = Column(String, nullable=False)
    resource_id = Column(String, nullable=False)
    permission_type = Column(Enum(PermissionType), nullable=False)
    granted_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="permissions")

class TeamPermission(Base):
    __tablename__ = "team_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    resource_type = Column(String, nullable=False)
    resource_id = Column(String, nullable=False)
    permission_type = Column(Enum(PermissionType), nullable=False)
    granted_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    team = relationship("Team", back_populates="permissions")
