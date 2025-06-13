from sqlalchemy import Column, Integer, String, DateTime, Text, Enum
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum as PyEnum
from .database import Base

class LogLevel(PyEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
class LogEvent(Base):
    __tablename__ = "log_events"
    
    id = Column(Integer, primary_key=True, index=True)
    message = Column(Text, nullable=False)
    level = Column(Enum(LogLevel), default=LogLevel.INFO)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    source = Column(String(255), nullable=True)
    log_metadata = Column(Text, nullable=True)  # Changed from 'metadata'
    
    def __repr__(self):
        return f"<LogEvent(id={self.id}, level={self.level}, message='{self.message[:50]}...')>"
