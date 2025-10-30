from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON, Enum, Time
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import enum
from .base import BaseModel

class NotificationChannel(enum.Enum):
    EMAIL = "email"
    SMS = "sms" 
    PUSH = "push"
    IN_APP = "in_app"
    WEBHOOK = "webhook"

class NotificationPriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class NotificationCategory(enum.Enum):
    SECURITY = "security"
    SYSTEM = "system"
    SOCIAL = "social"
    MARKETING = "marketing"
    UPDATES = "updates"

class NotificationPreference(BaseModel):
    __tablename__ = "notification_preferences"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_enabled = Column(Boolean, default=True)
    global_quiet_hours_enabled = Column(Boolean, default=False)
    
    user = relationship("User", backref="notification_preferences")

class ChannelPreference(BaseModel):
    __tablename__ = "channel_preferences"
    
    preference_id = Column(Integer, ForeignKey("notification_preferences.id"))
    channel = Column(Enum(NotificationCategory), nullable=False)
    priority_score = Column(Integer, default=50)  # 0-100 scale
    is_enabled = Column(Boolean, default=True)
    
    preference = relationship("NotificationPreference", backref="channel_preferences")

class QuietHours(BaseModel):
    __tablename__ = "quiet_hours"
    
    preference_id = Column(Integer, ForeignKey("notification_preferences.id"))
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    timezone = Column(String, default="UTC")
    days_of_week = Column(JSON)  # [0,1,2,3,4,5,6] for Sun-Sat
    exceptions = Column(JSON)  # Categories that override quiet hours
    
    preference = relationship("NotificationPreference", backref="quiet_hours")

class EscalationRule(BaseModel):
    __tablename__ = "escalation_rules"
    
    preference_id = Column(Integer, ForeignKey("notification_preferences.id"))
    category = Column(Enum(NotificationCategory), nullable=False)
    priority_threshold = Column(Enum(NotificationPriority), default=NotificationPriority.HIGH)
    escalation_delay_minutes = Column(Integer, default=15)
    escalation_channels = Column(JSON)  # Additional channels to try
    escalation_contacts = Column(JSON)  # Alternative contacts
    max_attempts = Column(Integer, default=3)
    
    preference = relationship("NotificationPreference", backref="escalation_rules")

class NotificationSubscription(BaseModel):
    __tablename__ = "notification_subscriptions"
    
    preference_id = Column(Integer, ForeignKey("notification_preferences.id"))
    category = Column(Enum(NotificationCategory), nullable=False)
    subcategory = Column(String, nullable=True)  # More granular control
    channels = Column(JSON)  # Preferred channels for this subscription
    is_subscribed = Column(Boolean, default=True)
    priority_override = Column(Integer, nullable=True)  # Override default priority
    
    preference = relationship("NotificationPreference", backref="subscriptions")
