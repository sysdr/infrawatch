from sqlalchemy import Column, String, DateTime, Boolean, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.database import Base

class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key_id = Column(String(64), unique=True, index=True, nullable=False)
    hashed_secret = Column(String(256), nullable=False)
    prefix = Column(String(16), nullable=False, default="sk_live")
    name = Column(String(128), nullable=False)
    description = Column(String(512))
    
    # Permissions and limits
    permissions = Column(JSON, default=list)
    rate_limit = Column(Integer, default=100)
    rate_window = Column(Integer, default=60)
    
    # IP whitelist (CIDR notation)
    ip_whitelist = Column(JSON, default=list)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_revoked = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    
    # Rotation
    rotated_from = Column(UUID(as_uuid=True), nullable=True)
    rotation_scheduled_at = Column(DateTime, nullable=True)
