from sqlalchemy import Column, String, JSON, Boolean
from .base import BaseModel

class Notification(BaseModel):
    __tablename__ = "notifications"
    
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    channel = Column(String, nullable=False)  # email, slack, webhook
    recipient = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, sent, failed
    meta_data = Column(JSON, default={})
    is_grouped = Column(Boolean, default=False)
    group_key = Column(String)
