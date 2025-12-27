from sqlalchemy import Column, Integer, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base

DEFAULT_PREFERENCES = {
    "theme": "light",
    "language": "en",
    "timezone": "UTC",
    "date_format": "YYYY-MM-DD",
    "time_format": "24h",
    "notifications": {
        "email": True,
        "push": True,
        "digest_frequency": "daily"
    },
    "dashboard": {
        "default_view": "overview",
        "widgets_per_page": 12,
        "refresh_interval": 30,
        "chart_theme": "default"
    },
    "privacy": {
        "profile_visibility": "team",
        "activity_tracking": True
    }
}

class UserPreference(Base):
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    preferences = Column(JSON, default=DEFAULT_PREFERENCES)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="preferences")
