from sqlalchemy import Column, Integer, String, DateTime, Boolean, LargeBinary, Enum as SQLEnum
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class DataClassification(enum.Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    email_encrypted = Column(LargeBinary)  # Encrypted version
    full_name = Column(String)
    full_name_encrypted = Column(LargeBinary)  # Encrypted version
    phone = Column(String)
    phone_encrypted = Column(LargeBinary)  # Encrypted version
    ssn_encrypted = Column(LargeBinary)  # Restricted data
    credit_card_encrypted = Column(LargeBinary)  # Restricted data
    classification = Column(SQLEnum(DataClassification), default=DataClassification.INTERNAL)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete for GDPR
    is_active = Column(Boolean, default=True)

class ConsentRecord(Base):
    __tablename__ = "consent_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    consent_bitfield = Column(Integer, default=0)  # Bitfield for 64 purposes
    granted_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    ip_address = Column(String)
    user_agent = Column(String)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    action = Column(String, nullable=False)  # access, modify, delete, export
    resource_type = Column(String)
    resource_id = Column(String)
    purpose = Column(String)  # Why data was accessed
    legal_basis = Column(String)  # consent, contract, legitimate_interest
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String)
    metadata_json = Column(String)  # JSON metadata

class GDPRRequest(Base):
    __tablename__ = "gdpr_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    request_type = Column(String)  # access, rectification, portability, erasure
    status = Column(String, default="pending")  # pending, processing, completed, failed
    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    result_location = Column(String, nullable=True)  # S3 path or file path
    error_message = Column(String, nullable=True)

class EncryptionKey(Base):
    __tablename__ = "encryption_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    key_id = Column(String, unique=True, index=True, nullable=False)
    encrypted_dek = Column(LargeBinary, nullable=False)  # Data Encryption Key encrypted with KEK
    algorithm = Column(String, default="AES-256-GCM")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    rotated_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
