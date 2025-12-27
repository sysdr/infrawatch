from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    
    # Basic info
    display_name = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    avatar_url = Column(String)
    bio = Column(Text)
    
    # Contact info
    phone = Column(String)
    location = Column(String)
    timezone = Column(String, default="UTC")
    
    # Professional info
    job_title = Column(String)
    department = Column(String)
    company = Column(String)
    
    # Custom fields (JSON)
    custom_fields = Column(JSON, default={})
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="profile")
