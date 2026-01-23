from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class ResourceState(enum.Enum):
    PENDING = "pending"
    VALIDATING = "validating"
    PROVISIONING = "provisioning"
    ACTIVE = "active"
    IDLE = "idle"
    DEPRECATED = "deprecated"
    FAILED = "failed"
    ARCHIVED = "archived"

class ResourceType(enum.Enum):
    COMPUTE = "compute"
    STORAGE = "storage"
    DATABASE = "database"
    NETWORK = "network"
    CONTAINER = "container"

class ComplianceStatus(enum.Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    WARNING = "warning"
    CHECKING = "checking"

class CloudResource(Base):
    __tablename__ = "cloud_resources"

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    resource_type = Column(SQLEnum(ResourceType))
    provider = Column(String)
    region = Column(String)
    state = Column(SQLEnum(ResourceState), default=ResourceState.PENDING)

    configuration = Column(JSON)
    template = Column(Text, nullable=True)

    hourly_cost = Column(Float, default=0.0)
    monthly_cost = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)

    cpu_utilization = Column(Float, default=0.0)
    memory_utilization = Column(Float, default=0.0)
    storage_utilization = Column(Float, default=0.0)
    network_utilization = Column(Float, default=0.0)

    created_at = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    scheduled_deletion = Column(DateTime, nullable=True)

    owner_id = Column(String)
    team = Column(String)

    tags = relationship("ResourceTag", back_populates="resource", cascade="all, delete-orphan")
    compliance_checks = relationship("ComplianceCheck", back_populates="resource", cascade="all, delete-orphan")
    cost_optimizations = relationship("CostOptimization", back_populates="resource", cascade="all, delete-orphan")
    lifecycle_events = relationship("LifecycleEvent", back_populates="resource", cascade="all, delete-orphan")

class ResourceTag(Base):
    __tablename__ = "resource_tags"

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("cloud_resources.id"))
    key = Column(String, index=True)
    value = Column(String)
    mandatory = Column(Boolean, default=False)
    auto_applied = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    resource = relationship("CloudResource", back_populates="tags")

class ComplianceRule(Base):
    __tablename__ = "compliance_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    resource_type = Column(SQLEnum(ResourceType))
    severity = Column(String)
    condition = Column(JSON)
    remediation = Column(Text)
    auto_remediate = Column(Boolean, default=False)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ComplianceCheck(Base):
    __tablename__ = "compliance_checks"

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("cloud_resources.id"))
    rule_id = Column(Integer, ForeignKey("compliance_rules.id"))
    status = Column(SQLEnum(ComplianceStatus), default=ComplianceStatus.CHECKING)
    details = Column(JSON)
    checked_at = Column(DateTime, default=datetime.utcnow)
    remediated = Column(Boolean, default=False)
    remediation_details = Column(Text, nullable=True)

    resource = relationship("CloudResource", back_populates="compliance_checks")
    rule = relationship("ComplianceRule")

class CostOptimization(Base):
    __tablename__ = "cost_optimizations"

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("cloud_resources.id"))
    optimization_type = Column(String)
    current_cost = Column(Float)
    optimized_cost = Column(Float)
    potential_savings = Column(Float)
    recommendation = Column(Text)
    confidence = Column(Float)
    applied = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    resource = relationship("CloudResource", back_populates="cost_optimizations")

class LifecyclePolicy(Base):
    __tablename__ = "lifecycle_policies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    resource_type = Column(SQLEnum(ResourceType))
    environment = Column(String)
    idle_threshold_days = Column(Integer, default=30)
    deletion_after_days = Column(Integer, default=90)
    notification_days = Column(JSON)
    require_approval = Column(Boolean, default=True)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class LifecycleEvent(Base):
    __tablename__ = "lifecycle_events"

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("cloud_resources.id"))
    event_type = Column(String)
    from_state = Column(String, nullable=True)
    to_state = Column(String, nullable=True)
    details = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    resource = relationship("CloudResource", back_populates="lifecycle_events")

class ProvisioningTemplate(Base):
    __tablename__ = "provisioning_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    template_type = Column(String)
    content = Column(Text)
    variables = Column(JSON)
    version = Column(String)
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
