from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class UserStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEPROVISIONED = "deprovisioned"

class ProvisioningMethod(str, enum.Enum):
    MANUAL = "manual"
    LDAP_SYNC = "ldap_sync"
    SSO_JIT = "sso_jit"
    SCIM = "scim"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255))
    department = Column(String(100))
    employee_type = Column(String(50))
    manager = Column(String(100))
    status = Column(SQLEnum(UserStatus), default=UserStatus.PENDING)
    provisioning_method = Column(SQLEnum(ProvisioningMethod), default=ProvisioningMethod.MANUAL)
    ldap_dn = Column(String(500))
    saml_nameid = Column(String(255))
    is_ldap_synced = Column(Boolean, default=False)
    last_ldap_sync = Column(DateTime)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deprovisioned_at = Column(DateTime)
    
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")

class LDAPConfig(Base):
    __tablename__ = "ldap_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    server = Column(String(255), nullable=False)
    base_dn = Column(String(500), nullable=False)
    bind_dn = Column(String(500), nullable=False)
    bind_password = Column(Text, nullable=False)
    user_filter = Column(String(255), default="(objectClass=inetOrgPerson)")
    sync_enabled = Column(Boolean, default=True)
    sync_interval_minutes = Column(Integer, default=30)
    last_sync = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class SAMLConfig(Base):
    __tablename__ = "saml_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    entity_id = Column(String(255), nullable=False)
    sso_url = Column(String(500), nullable=False)
    x509_cert = Column(Text, nullable=False)
    attribute_mapping = Column(Text)
    jit_provisioning = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ImportJob(Base):
    __tablename__ = "import_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    total_users = Column(Integer, default=0)
    processed = Column(Integer, default=0)
    created_count = Column(Integer, default=0)
    updated_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    status = Column(String(50), default="pending")
    error_log = Column(Text)
    initiated_by = Column(String(100))
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    details = Column(Text)
    performed_by = Column(String(100))
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="audit_logs")
