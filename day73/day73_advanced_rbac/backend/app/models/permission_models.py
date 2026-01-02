from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, Index, text
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from . import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(Text)
    parent_role_id = Column(Integer, nullable=True)  # For role hierarchy
    created_at = Column(DateTime, default=datetime.utcnow)

class Team(Base):
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text)
    parent_team_id = Column(Integer, nullable=True)  # For team hierarchy
    created_at = Column(DateTime, default=datetime.utcnow)

class UserRole(Base):
    __tablename__ = "user_roles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    role_id = Column(Integer, nullable=False, index=True)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    assigned_by = Column(Integer)  # user_id who assigned

class TeamMember(Base):
    __tablename__ = "team_members"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    joined_at = Column(DateTime, default=datetime.utcnow)

class PermissionPolicy(Base):
    __tablename__ = "permission_policies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False)
    subject_type = Column(String(20), nullable=False)  # user, role, team
    subject_id = Column(String(100), nullable=False)
    action = Column(String(50), nullable=False)  # read, write, delete, admin
    resource_type = Column(String(50), nullable=False)  # project, dashboard, alert
    resource_id = Column(String(100))  # specific resource or * for all
    effect = Column(String(10), nullable=False)  # allow, deny
    conditions = Column(JSONB)  # time, location, approval requirements
    priority = Column(Integer, default=0)  # Higher priority wins
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_policy_subject', 'subject_type', 'subject_id'),
        Index('idx_policy_resource', 'resource_type', 'resource_id'),
        Index('idx_policy_action', 'action'),
    )

class Resource(Base):
    __tablename__ = "resources"
    
    id = Column(Integer, primary_key=True, index=True)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(100), nullable=False)
    owner_id = Column(Integer)  # user who owns this resource
    resource_metadata = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_resource_lookup', 'resource_type', 'resource_id'),
    )

# Partitioned audit table - base definition
class AuditEvent(Base):
    __tablename__ = "audit_events"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    subject_type = Column(String(20), nullable=False)
    subject_id = Column(String(100), nullable=False)
    action = Column(String(50), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(100))
    decision = Column(String(20), nullable=False)  # allowed, denied
    reason = Column(Text)
    policy_matched = Column(String(200))
    context = Column(JSONB)
    
    __table_args__ = (
        Index('idx_audit_timestamp', 'timestamp'),
        Index('idx_audit_subject', 'subject_type', 'subject_id'),
        Index('idx_audit_resource', 'resource_type', 'resource_id'),
    )

class ComplianceViolation(Base):
    __tablename__ = "compliance_violations"
    
    id = Column(Integer, primary_key=True, index=True)
    violation_type = Column(String(100), nullable=False)
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    subject_id = Column(String(100), nullable=False)
    description = Column(Text)
    detected_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)
    resolution_notes = Column(Text)
    violation_metadata = Column(JSONB)
