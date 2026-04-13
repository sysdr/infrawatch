from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
from app.database import Base

def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)

class User(Base):
    __tablename__ = "users"
    id         = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username   = Column(String(50), unique=True, nullable=False)
    email      = Column(String(100), unique=True, nullable=False)
    role       = Column(String(20), default="engineer")
    timezone   = Column(String(50), default="UTC")
    created_at = Column(DateTime, default=utcnow)
    subscriptions = relationship("PushSubscription",       back_populates="user", cascade="all, delete-orphan")
    preferences   = relationship("NotificationPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")

class PushSubscription(Base):
    __tablename__ = "push_subscriptions"
    id         = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id    = Column(String, ForeignKey("users.id"), nullable=False)
    endpoint   = Column(Text, nullable=False)
    p256dh     = Column(Text, nullable=False)
    auth       = Column(Text, nullable=False)
    user_agent = Column(String(200))
    is_active  = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)
    last_used  = Column(DateTime)
    user       = relationship("User", back_populates="subscriptions")

class NotificationPreference(Base):
    __tablename__ = "notification_preferences"
    id                      = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id                 = Column(String, ForeignKey("users.id"), nullable=False, unique=True)
    alerts_enabled          = Column(Boolean, default=True)
    team_updates_enabled    = Column(Boolean, default=True)
    daily_digest_enabled    = Column(Boolean, default=True)
    security_events_enabled = Column(Boolean, default=True)
    quiet_hours_start       = Column(Integer, default=22)
    quiet_hours_end         = Column(Integer, default=8)
    quiet_hours_enabled     = Column(Boolean, default=False)
    snoozed_until           = Column(DateTime, nullable=True)
    updated_at              = Column(DateTime, default=utcnow, onupdate=utcnow)
    user                    = relationship("User", back_populates="preferences")

class Notification(Base):
    __tablename__ = "notifications"
    id           = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id      = Column(String, ForeignKey("users.id"), nullable=False)
    category     = Column(String(50), nullable=False)
    title        = Column(String(200), nullable=False)
    body         = Column(Text, nullable=False)
    url          = Column(String(500), default="/")
    sent_at      = Column(DateTime, default=utcnow)
    delivered_at = Column(DateTime)
    clicked_at   = Column(DateTime)
    dismissed_at = Column(DateTime)
    status       = Column(String(20), default="sent")
    extra_data   = Column(JSON, default=dict)

class NotificationEvent(Base):
    __tablename__    = "notification_events"
    id               = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    notification_id  = Column(String, ForeignKey("notifications.id"), nullable=False)
    event_type       = Column(String(30), nullable=False)
    occurred_at      = Column(DateTime, default=utcnow)
    event_metadata   = Column(JSON, default=dict)
