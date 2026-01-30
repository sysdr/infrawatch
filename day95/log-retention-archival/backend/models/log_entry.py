from sqlalchemy import Column, String, Integer, DateTime, Enum, Float, JSON, Boolean
from sqlalchemy.sql import func
from models.database import Base
import enum

class StorageTier(str, enum.Enum):
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"
    DELETED = "deleted"

class ComplianceFramework(str, enum.Enum):
    SOC2 = "SOC2"
    HIPAA = "HIPAA"
    GDPR = "GDPR"
    PCI_DSS = "PCI_DSS"
    NONE = "NONE"

class LogEntry(Base):
    __tablename__ = "log_entries"
    
    id = Column(String, primary_key=True)
    source = Column(String, index=True)
    level = Column(String, index=True)
    message = Column(String)
    timestamp = Column(DateTime(timezone=True), index=True)
    storage_tier = Column(Enum(StorageTier), default=StorageTier.HOT, index=True)
    storage_path = Column(String)
    original_size = Column(Integer)
    compressed_size = Column(Integer)
    compression_ratio = Column(Float)
    checksum = Column(String)
    compliance_tags = Column(JSON)
    retention_until = Column(DateTime(timezone=True), index=True)
    last_accessed = Column(DateTime(timezone=True))
    query_count = Column(Integer, default=0)
    archived_at = Column(DateTime(timezone=True))
    deleted_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class RetentionPolicy(Base):
    __tablename__ = "retention_policies"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    log_source_pattern = Column(String)
    log_level_pattern = Column(String)
    hot_retention_days = Column(Integer)
    warm_retention_days = Column(Integer)
    cold_retention_days = Column(Integer)
    compliance_frameworks = Column(JSON)
    auto_delete = Column(Boolean, default=True)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ArchivalJob(Base):
    __tablename__ = "archival_jobs"
    
    id = Column(Integer, primary_key=True)
    job_type = Column(String)  # transition, compression, deletion
    status = Column(String)  # pending, running, completed, failed
    source_tier = Column(Enum(StorageTier))
    target_tier = Column(Enum(StorageTier))
    log_count = Column(Integer)
    data_size = Column(Integer)
    compressed_size = Column(Integer)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    error_message = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ComplianceAudit(Base):
    __tablename__ = "compliance_audits"
    
    id = Column(Integer, primary_key=True)
    log_id = Column(String, index=True)
    action = Column(String)  # created, transitioned, accessed, deleted
    actor = Column(String)
    storage_tier = Column(Enum(StorageTier))
    compliance_check = Column(Boolean)
    extra_metadata = Column(JSON)  # renamed from 'metadata' (reserved in SQLAlchemy Declarative)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class StorageMetrics(Base):
    __tablename__ = "storage_metrics"
    
    id = Column(Integer, primary_key=True)
    tier = Column(Enum(StorageTier))
    log_count = Column(Integer)
    total_size = Column(Integer)
    compressed_size = Column(Integer)
    cost_per_gb = Column(Float)
    total_cost = Column(Float)
    snapshot_time = Column(DateTime(timezone=True), server_default=func.now())
