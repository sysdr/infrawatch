from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class NotificationStatus(enum.Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    RETRY = "retry"
    FAILED_PERMANENT = "failed_permanent"

class NotificationChannel(enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"

class NotificationPriority(enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    channel = Column(Enum(NotificationChannel), nullable=False)
    priority = Column(Enum(NotificationPriority), default=NotificationPriority.NORMAL)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.QUEUED)
    
    # Content
    subject = Column(String(255))
    content = Column(Text, nullable=False)
    template_id = Column(String(100))
    template_data = Column(JSON)
    
    # Delivery details
    recipient = Column(String(255), nullable=False)
    sender = Column(String(255))
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow)
    scheduled_at = Column(DateTime)
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    read_at = Column(DateTime)
    
    # Retry tracking
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    next_retry_at = Column(DateTime)
    
    # Failure tracking
    error_message = Column(Text)
    error_code = Column(String(50))
    
    # Metadata
    metadata = Column(JSON)
    tracking_id = Column(String(100), unique=True, index=True)

class DeliveryAttempt(Base):
    __tablename__ = "delivery_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(Integer, nullable=False, index=True)
    attempt_number = Column(Integer, nullable=False)
    
    # Attempt details
    attempted_at = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(NotificationStatus), nullable=False)
    
    # Timing
    processing_time_ms = Column(Float)
    
    # Results
    success = Column(Boolean, default=False)
    error_message = Column(Text)
    error_code = Column(String(50))
    
    # Response data
    response_data = Column(JSON)
    
    # Metadata
    server_id = Column(String(50))
    metadata = Column(JSON)

class RateLimitEntry(Base):
    __tablename__ = "rate_limits"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    channel = Column(Enum(NotificationChannel), nullable=False)
    
    # Rate limiting
    count = Column(Integer, default=0)
    window_start = Column(DateTime, default=datetime.utcnow)
    window_end = Column(DateTime, nullable=False)
    limit_value = Column(Integer, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
