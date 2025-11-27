from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class ReportFormat(str, enum.Enum):
    HTML = "html"
    PDF = "pdf"
    BOTH = "both"

class ReportStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class DeliveryStatus(str, enum.Enum):
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"
    OPENED = "opened"
    CLICKED = "clicked"

class Template(Base):
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    content = Column(Text, nullable=False)
    format = Column(SQLEnum(ReportFormat), default=ReportFormat.HTML)
    variables = Column(JSON, default=list)
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    scheduled_reports = relationship("ScheduledReport", back_populates="template")

class ScheduledReport(Base):
    __tablename__ = "scheduled_reports"
    
    id = Column(Integer, primary_key=True)
    template_id = Column(Integer, ForeignKey("templates.id"))
    name = Column(String(255), nullable=False)
    schedule_cron = Column(String(100), nullable=False)
    recipients = Column(JSON, default=list)
    config = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    last_run = Column(DateTime)
    next_run = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    template = relationship("Template", back_populates="scheduled_reports")
    executions = relationship("ReportExecution", back_populates="scheduled_report")

class ReportExecution(Base):
    __tablename__ = "report_executions"
    
    id = Column(Integer, primary_key=True)
    scheduled_report_id = Column(Integer, ForeignKey("scheduled_reports.id"))
    status = Column(SQLEnum(ReportStatus), default=ReportStatus.PENDING)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    output_file = Column(String(500))
    output_format = Column(String(10))
    error_message = Column(Text)
    execution_time = Column(Integer)  # seconds
    
    scheduled_report = relationship("ScheduledReport", back_populates="executions")
    deliveries = relationship("EmailDelivery", back_populates="execution")

class EmailDelivery(Base):
    __tablename__ = "email_deliveries"
    
    id = Column(Integer, primary_key=True)
    execution_id = Column(Integer, ForeignKey("report_executions.id"))
    recipient = Column(String(255), nullable=False)
    status = Column(SQLEnum(DeliveryStatus), default=DeliveryStatus.QUEUED)
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    opened_at = Column(DateTime)
    clicked_at = Column(DateTime)
    error_message = Column(Text)
    sendgrid_message_id = Column(String(255))
    
    execution = relationship("ReportExecution", back_populates="deliveries")
