from sqlalchemy import Column, String, Boolean, Integer, DateTime, Text, JSON, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MFAConfig(Base):
    __tablename__ = "mfa_configs"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    totp_secret = Column(Text)
    backup_codes = Column(JSONB)
    sms_enabled = Column(Boolean, default=False)
    phone_number = Column(String(20))
    enabled_at = Column(DateTime)
    verified_at = Column(DateTime)

class Device(Base):
    __tablename__ = "devices"
    
    device_id = Column(String(64), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    fingerprint = Column(JSONB)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    trust_score = Column(Integer, default=50)
    login_count = Column(Integer, default=0)
    ip_addresses = Column(ARRAY(String))
    user_agent = Column(Text)

class OAuthClient(Base):
    __tablename__ = "oauth_clients"
    
    client_id = Column(String(64), primary_key=True)
    client_secret = Column(Text, nullable=False)
    client_name = Column(String(255), nullable=False)
    redirect_uris = Column(JSONB, nullable=False)
    allowed_scopes = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)

class OAuthCode(Base):
    __tablename__ = "oauth_codes"
    
    code = Column(String(128), primary_key=True)
    client_id = Column(String(64), ForeignKey("oauth_clients.client_id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    code_challenge = Column(String(128))
    code_challenge_method = Column(String(10))
    redirect_uri = Column(Text)
    scope = Column(String(500))
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class RiskEvent(Base):
    __tablename__ = "risk_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    risk_score = Column(Integer)
    factors = Column(JSONB)
    action_taken = Column(String(50))
    ip_address = Column(String(45))
    device_id = Column(String(64))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
