from sqlalchemy import Column, Integer, String, JSON, DateTime, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class Integration(Base):
    __tablename__ = "integrations"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # webhook, api, etc.
    config = Column(JSON, default={})
    enabled = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

class WebhookEvent(Base):
    __tablename__ = "webhook_events"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    integration_id = Column(String(36), nullable=False, index=True)
    source = Column(String(255))
    payload = Column(JSON, default={})
    processed = Column(Integer, default=0)  # 0 pending, 1 processed
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
