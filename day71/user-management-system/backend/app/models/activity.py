from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Text, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..core.database import Base

class ActivityType(str, enum.Enum):
    AUTH_LOGIN = "auth.login"
    AUTH_LOGOUT = "auth.logout"
    AUTH_FAILED = "auth.failed"
    PROFILE_UPDATED = "profile.updated"
    PREFERENCE_UPDATED = "preference.updated"
    DASHBOARD_CREATED = "dashboard.created"
    DASHBOARD_VIEWED = "dashboard.viewed"
    DASHBOARD_UPDATED = "dashboard.updated"
    DASHBOARD_DELETED = "dashboard.deleted"
    EXPORT_GENERATED = "export.generated"
    SETTING_CHANGED = "setting.changed"

class UserActivity(Base):
    __tablename__ = "user_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    action = Column(String, nullable=False)
    resource_type = Column(String)
    resource_id = Column(Integer)
    description = Column(Text)
    activity_metadata = Column(JSON, default={})
    ip_address = Column(String)
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship
    user = relationship("User", back_populates="activities")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_user_activity_created', 'user_id', 'created_at'),
        Index('idx_activity_type_created', 'action', 'created_at'),
    )
