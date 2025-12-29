from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Boolean, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    settings = Column(JSON, default={})
    
    teams = relationship("Team", back_populates="organization", cascade="all, delete-orphan")

class Team(Base):
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"))
    parent_team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), index=True)
    description = Column(Text)
    materialized_path = Column(String(1000), index=True)
    member_count = Column(Integer, default=0)
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    team_metadata = Column("metadata", JSON, default={}, key="team_metadata")
    
    organization = relationship("Organization", back_populates="teams")
    parent_team = relationship("Team", remote_side=[id], backref="sub_teams")
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    permissions = relationship("TeamPermission", back_populates="team", cascade="all, delete-orphan")

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    permissions = Column(JSON, default=[])
    is_system_role = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class TeamMember(Base):
    __tablename__ = "team_members"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    role_id = Column(Integer, ForeignKey("roles.id"))
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    invited_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    effective_permissions = Column(JSON, default=[])
    
    team = relationship("Team", back_populates="members")
    user = relationship("User", foreign_keys=[user_id])
    role = relationship("Role")
    inviter = relationship("User", foreign_keys=[invited_by])

class TeamPermission(Base):
    __tablename__ = "team_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"))
    resource_type = Column(String(100))
    resource_id = Column(Integer, nullable=True)
    permission_type = Column(String(100))
    allow = Column(Boolean, default=True)
    
    team = relationship("Team", back_populates="permissions")

class TeamActivity(Base):
    __tablename__ = "team_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    activity_type = Column(String(100))
    description = Column(Text)
    activity_metadata = Column("metadata", JSON, default={}, key="activity_metadata")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    username = Column(String(100), unique=True, index=True)
    full_name = Column(String(255))
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
