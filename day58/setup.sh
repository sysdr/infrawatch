#!/bin/bash

# Day 58: Report Templates - Complete Project Setup Script
# This script creates a production-ready report template system

set -e  # Exit on error

PROJECT_NAME="report-templates-system"
BASE_DIR=$(pwd)/$PROJECT_NAME

echo "=================================================="
echo "Day 58: Report Templates System Setup"
echo "=================================================="

# Create project structure
echo "Creating project structure..."
mkdir -p $PROJECT_NAME/{backend/{app/{api,models,services,templates,utils},tests},frontend/{src/{components,pages,services,utils},public},docker,outputs,sample-templates}
cd $PROJECT_NAME

# Backend Requirements
cat > backend/requirements.txt << 'EOF'
fastapi==0.115.0
uvicorn[standard]==0.32.0
sqlalchemy==2.0.35
psycopg2-binary==2.9.10
alembic==1.14.0
redis==5.2.0
celery==5.4.0
apscheduler==3.10.4
jinja2==3.1.4
weasyprint==62.3
sendgrid==6.11.0
python-multipart==0.0.12
python-dotenv==1.0.1
pydantic==2.9.2
pydantic-settings==2.6.0
httpx==0.27.2
pytest==8.3.3
pytest-asyncio==0.24.0
pytest-cov==6.0.0
EOF

# Backend .env
cat > backend/.env << 'EOF'
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/reports_db
REDIS_URL=redis://localhost:6379/0
SENDGRID_API_KEY=test_key_for_demo
STORAGE_PATH=../outputs
TEMPLATE_PATH=../sample-templates
SECRET_KEY=dev-secret-key-change-in-production
ENV=development
EOF

# Backend Database Models
cat > backend/app/models/__init__.py << 'EOF'
from .template import Template, ScheduledReport, ReportExecution, EmailDelivery

__all__ = ['Template', 'ScheduledReport', 'ReportExecution', 'EmailDelivery']
EOF

cat > backend/app/models/template.py << 'EOF'
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
EOF

# Database connection
cat > backend/app/database.py << 'EOF'
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.template import Base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/reports_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
EOF

# Template Service
cat > backend/app/services/__init__.py << 'EOF'
from .template_service import TemplateService
from .report_service import ReportService
from .email_service import EmailService
from .scheduler_service import SchedulerService

__all__ = ['TemplateService', 'ReportService', 'EmailService', 'SchedulerService']
EOF

cat > backend/app/services/template_service.py << 'EOF'
from sqlalchemy.orm import Session
from app.models.template import Template, ReportFormat
from jinja2 import Environment, BaseLoader, TemplateSyntaxError
from typing import Dict, Any, List
import re

class TemplateService:
    
    @staticmethod
    def create_template(db: Session, name: str, content: str, 
                       format: ReportFormat = ReportFormat.HTML,
                       description: str = None, variables: List[str] = None) -> Template:
        """Create a new template"""
        # Extract variables from template if not provided
        if variables is None:
            variables = TemplateService.extract_variables(content)
        
        template = Template(
            name=name,
            description=description,
            content=content,
            format=format,
            variables=variables,
            version=1
        )
        db.add(template)
        db.commit()
        db.refresh(template)
        return template
    
    @staticmethod
    def extract_variables(content: str) -> List[str]:
        """Extract Jinja2 variables from template content"""
        pattern = r'\{\{\s*([a-zA-Z_][a-zA-Z0-9_\.]*)\s*\}\}'
        matches = re.findall(pattern, content)
        return list(set(matches))
    
    @staticmethod
    def validate_template(content: str) -> tuple[bool, str]:
        """Validate Jinja2 template syntax"""
        try:
            env = Environment(loader=BaseLoader())
            env.parse(content)
            return True, "Template is valid"
        except TemplateSyntaxError as e:
            return False, str(e)
    
    @staticmethod
    def render_template(template: Template, data: Dict[str, Any]) -> str:
        """Render template with data"""
        env = Environment(loader=BaseLoader())
        jinja_template = env.from_string(template.content)
        return jinja_template.render(**data)
    
    @staticmethod
    def get_all_templates(db: Session, active_only: bool = False) -> List[Template]:
        """Get all templates"""
        query = db.query(Template)
        if active_only:
            query = query.filter(Template.is_active == True)
        return query.order_by(Template.created_at.desc()).all()
    
    @staticmethod
    def get_template(db: Session, template_id: int) -> Template:
        """Get template by ID"""
        return db.query(Template).filter(Template.id == template_id).first()
    
    @staticmethod
    def update_template(db: Session, template_id: int, **kwargs) -> Template:
        """Update template (creates new version)"""
        template = db.query(Template).filter(Template.id == template_id).first()
        if not template:
            return None
        
        # Create new version
        new_version = template.version + 1
        for key, value in kwargs.items():
            if hasattr(template, key):
                setattr(template, key, value)
        template.version = new_version
        
        db.commit()
        db.refresh(template)
        return template
    
    @staticmethod
    def delete_template(db: Session, template_id: int) -> bool:
        """Soft delete template"""
        template = db.query(Template).filter(Template.id == template_id).first()
        if template:
            template.is_active = False
            db.commit()
            return True
        return False
EOF

cat > backend/app/services/report_service.py << 'EOF'
from sqlalchemy.orm import Session
from app.models.template import ScheduledReport, ReportExecution, ReportStatus, Template
from app.services.template_service import TemplateService
from datetime import datetime, timedelta
from typing import Dict, Any
import os
from weasyprint import HTML
import json

class ReportService:
    
    @staticmethod
    def create_scheduled_report(db: Session, template_id: int, name: str,
                               schedule_cron: str, recipients: list,
                               config: dict = None) -> ScheduledReport:
        """Create a scheduled report"""
        scheduled_report = ScheduledReport(
            template_id=template_id,
            name=name,
            schedule_cron=schedule_cron,
            recipients=recipients,
            config=config or {},
            next_run=ReportService.calculate_next_run(schedule_cron)
        )
        db.add(scheduled_report)
        db.commit()
        db.refresh(scheduled_report)
        return scheduled_report
    
    @staticmethod
    def calculate_next_run(cron_expression: str) -> datetime:
        """Calculate next run time from cron expression"""
        # Simplified for demo - in production use croniter
        return datetime.utcnow() + timedelta(hours=24)
    
    @staticmethod
    def generate_report(db: Session, scheduled_report_id: int,
                       data: Dict[str, Any] = None) -> ReportExecution:
        """Generate a report"""
        scheduled_report = db.query(ScheduledReport).filter(
            ScheduledReport.id == scheduled_report_id
        ).first()
        
        if not scheduled_report:
            raise ValueError("Scheduled report not found")
        
        # Create execution record
        execution = ReportExecution(
            scheduled_report_id=scheduled_report_id,
            status=ReportStatus.PROCESSING,
            started_at=datetime.utcnow()
        )
        db.add(execution)
        db.commit()
        
        try:
            # Get template
            template = scheduled_report.template
            
            # Generate sample data if not provided
            if data is None:
                data = ReportService.generate_sample_data(scheduled_report.config)
            
            # Render template
            html_content = TemplateService.render_template(template, data)
            
            # Save output
            output_dir = os.getenv("STORAGE_PATH", "../outputs")
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            base_filename = f"report_{execution.id}_{timestamp}"
            
            # Save HTML
            html_file = f"{output_dir}/{base_filename}.html"
            with open(html_file, 'w') as f:
                f.write(html_content)
            
            execution.output_file = html_file
            execution.output_format = "html"
            
            # Generate PDF if needed
            if template.format in ["pdf", "both"]:
                pdf_file = f"{output_dir}/{base_filename}.pdf"
                HTML(string=html_content).write_pdf(pdf_file)
                execution.output_file = pdf_file
                execution.output_format = "pdf"
            
            # Mark as completed
            execution.status = ReportStatus.COMPLETED
            execution.completed_at = datetime.utcnow()
            execution.execution_time = int((execution.completed_at - execution.started_at).total_seconds())
            
            # Update scheduled report
            scheduled_report.last_run = datetime.utcnow()
            scheduled_report.next_run = ReportService.calculate_next_run(scheduled_report.schedule_cron)
            
            db.commit()
            db.refresh(execution)
            return execution
            
        except Exception as e:
            execution.status = ReportStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
            db.commit()
            raise
    
    @staticmethod
    def generate_sample_data(config: dict) -> Dict[str, Any]:
        """Generate sample data for report"""
        return {
            "company_name": "TechCorp Inc.",
            "report_type": "Weekly Summary",
            "date_range": "Nov 18-24, 2025",
            "recipient_name": "Team",
            "total_alerts": 1247,
            "critical_alerts": 23,
            "warning_alerts": 156,
            "info_alerts": 1068,
            "top_services": [
                {"name": "API Gateway", "count": 342, "severity": "critical"},
                {"name": "Database Cluster", "count": 289, "severity": "warning"},
                {"name": "Cache Service", "count": 234, "severity": "info"}
            ],
            "performance_metrics": {
                "avg_response_time": "245ms",
                "uptime": "99.94%",
                "error_rate": "0.12%"
            },
            "trends": {
                "alerts_vs_last_week": "+15%",
                "response_time_change": "-8%",
                "uptime_change": "+0.02%"
            }
        }
    
    @staticmethod
    def get_executions(db: Session, scheduled_report_id: int = None,
                      status: ReportStatus = None, limit: int = 100):
        """Get report executions"""
        query = db.query(ReportExecution)
        if scheduled_report_id:
            query = query.filter(ReportExecution.scheduled_report_id == scheduled_report_id)
        if status:
            query = query.filter(ReportExecution.status == status)
        return query.order_by(ReportExecution.started_at.desc()).limit(limit).all()
EOF

cat > backend/app/services/email_service.py << 'EOF'
from sqlalchemy.orm import Session
from app.models.template import EmailDelivery, DeliveryStatus, ReportExecution
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import base64
import os
from datetime import datetime
import time

class EmailService:
    
    def __init__(self):
        self.api_key = os.getenv("SENDGRID_API_KEY")
        self.from_email = "reports@example.com"
    
    def send_report(self, db: Session, execution_id: int, recipients: list) -> list:
        """Send report via email to recipients"""
        execution = db.query(ReportExecution).filter(
            ReportExecution.id == execution_id
        ).first()
        
        if not execution or not execution.output_file:
            raise ValueError("Execution not found or report not generated")
        
        delivery_results = []
        
        for recipient in recipients:
            delivery = EmailDelivery(
                execution_id=execution_id,
                recipient=recipient,
                status=DeliveryStatus.QUEUED
            )
            db.add(delivery)
            db.commit()
            db.refresh(delivery)
            
            try:
                # Send email with retry logic
                success = self._send_with_retry(execution, recipient)
                
                if success:
                    delivery.status = DeliveryStatus.SENT
                    delivery.sent_at = datetime.utcnow()
                else:
                    delivery.status = DeliveryStatus.FAILED
                    delivery.error_message = "Failed to send after retries"
                
                db.commit()
                delivery_results.append(delivery)
                
            except Exception as e:
                delivery.status = DeliveryStatus.FAILED
                delivery.error_message = str(e)
                db.commit()
                delivery_results.append(delivery)
        
        return delivery_results
    
    def _send_with_retry(self, execution: ReportExecution, recipient: str,
                        max_retries: int = 3) -> bool:
        """Send email with exponential backoff retry"""
        for attempt in range(max_retries):
            try:
                return self._send_email(execution, recipient)
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 1s, 2s, 4s
                    time.sleep(wait_time)
                else:
                    raise
        return False
    
    def _send_email(self, execution: ReportExecution, recipient: str) -> bool:
        """Send single email"""
        # For demo, just log instead of actually sending
        print(f"[EMAIL] Sending report to {recipient}")
        print(f"[EMAIL] Report file: {execution.output_file}")
        
        # In production, use SendGrid:
        # message = Mail(
        #     from_email=self.from_email,
        #     to_emails=recipient,
        #     subject=f"Report: {execution.scheduled_report.name}",
        #     html_content=self._generate_email_body(execution)
        # )
        # 
        # # Attach report file
        # with open(execution.output_file, 'rb') as f:
        #     data = f.read()
        # encoded = base64.b64encode(data).decode()
        # attachment = Attachment(
        #     FileContent(encoded),
        #     FileName(os.path.basename(execution.output_file)),
        #     FileType('application/pdf'),
        #     Disposition('attachment')
        # )
        # message.attachment = attachment
        # 
        # sg = SendGridAPIClient(self.api_key)
        # response = sg.send(message)
        # return response.status_code == 202
        
        return True  # Demo mode
    
    def _generate_email_body(self, execution: ReportExecution) -> str:
        """Generate email body HTML"""
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Your Report is Ready</h2>
            <p>Please find your scheduled report attached.</p>
            <p><strong>Report:</strong> {execution.scheduled_report.name}</p>
            <p><strong>Generated:</strong> {execution.completed_at}</p>
            <p><strong>Execution Time:</strong> {execution.execution_time}s</p>
            <hr>
            <p style="font-size: 12px; color: #666;">
                To unsubscribe from these reports, click 
                <a href="#">here</a>
            </p>
        </body>
        </html>
        """
EOF

cat > backend/app/services/scheduler_service.py << 'EOF'
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.template import ScheduledReport
from app.services.report_service import ReportService
from app.services.email_service import EmailService
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SchedulerService:
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.email_service = EmailService()
    
    def start(self):
        """Start the scheduler"""
        self.scheduler.add_job(
            self.check_scheduled_reports,
            'interval',
            minutes=1,
            id='check_scheduled_reports'
        )
        self.scheduler.start()
        logger.info("Scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")
    
    def check_scheduled_reports(self):
        """Check for reports that need to be generated"""
        db = SessionLocal()
        try:
            now = datetime.utcnow()
            due_reports = db.query(ScheduledReport).filter(
                ScheduledReport.is_active == True,
                ScheduledReport.next_run <= now
            ).all()
            
            logger.info(f"Found {len(due_reports)} reports due for generation")
            
            for report in due_reports:
                try:
                    # Generate report
                    execution = ReportService.generate_report(db, report.id)
                    logger.info(f"Generated report {report.name} (execution_id={execution.id})")
                    
                    # Send emails
                    deliveries = self.email_service.send_report(
                        db, execution.id, report.recipients
                    )
                    logger.info(f"Sent report to {len(deliveries)} recipients")
                    
                except Exception as e:
                    logger.error(f"Failed to process report {report.id}: {str(e)}")
        
        finally:
            db.close()
EOF

# API Routes
cat > backend/app/api/__init__.py << 'EOF'
from .templates import router as templates_router
from .reports import router as reports_router

__all__ = ['templates_router', 'reports_router']
EOF

cat > backend/app/api/templates.py << 'EOF'
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.template_service import TemplateService
from app.models.template import ReportFormat
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api/templates", tags=["templates"])

class TemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    content: str
    format: ReportFormat = ReportFormat.HTML

class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    format: Optional[ReportFormat] = None

class PreviewRequest(BaseModel):
    data: dict

@router.post("/")
def create_template(template: TemplateCreate, db: Session = Depends(get_db)):
    """Create a new template"""
    # Validate template
    is_valid, message = TemplateService.validate_template(template.content)
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)
    
    result = TemplateService.create_template(
        db,
        name=template.name,
        description=template.description,
        content=template.content,
        format=template.format
    )
    return {
        "id": result.id,
        "name": result.name,
        "version": result.version,
        "variables": result.variables
    }

@router.get("/")
def get_templates(active_only: bool = False, db: Session = Depends(get_db)):
    """Get all templates"""
    templates = TemplateService.get_all_templates(db, active_only)
    return [
        {
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "format": t.format,
            "version": t.version,
            "variables": t.variables,
            "created_at": t.created_at.isoformat()
        }
        for t in templates
    ]

@router.get("/{template_id}")
def get_template(template_id: int, db: Session = Depends(get_db)):
    """Get template by ID"""
    template = TemplateService.get_template(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return {
        "id": template.id,
        "name": template.name,
        "description": template.description,
        "content": template.content,
        "format": template.format,
        "variables": template.variables,
        "version": template.version
    }

@router.post("/{template_id}/preview")
def preview_template(template_id: int, request: PreviewRequest, db: Session = Depends(get_db)):
    """Preview template with data"""
    template = TemplateService.get_template(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    try:
        rendered = TemplateService.render_template(template, request.data)
        return {"html": rendered}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Rendering error: {str(e)}")

@router.put("/{template_id}")
def update_template(template_id: int, updates: TemplateUpdate, db: Session = Depends(get_db)):
    """Update template"""
    update_data = updates.dict(exclude_unset=True)
    
    # Validate content if provided
    if 'content' in update_data:
        is_valid, message = TemplateService.validate_template(update_data['content'])
        if not is_valid:
            raise HTTPException(status_code=400, detail=message)
    
    template = TemplateService.update_template(db, template_id, **update_data)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return {"id": template.id, "version": template.version}

@router.delete("/{template_id}")
def delete_template(template_id: int, db: Session = Depends(get_db)):
    """Delete template"""
    success = TemplateService.delete_template(db, template_id)
    if not success:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"message": "Template deleted"}
EOF

cat > backend/app/api/reports.py << 'EOF'
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.report_service import ReportService
from app.services.email_service import EmailService
from pydantic import BaseModel
from typing import List, Optional
import os

router = APIRouter(prefix="/api/reports", tags=["reports"])

class ScheduledReportCreate(BaseModel):
    template_id: int
    name: str
    schedule_cron: str
    recipients: List[str]
    config: Optional[dict] = None

class GenerateReportRequest(BaseModel):
    template_id: Optional[int] = None
    scheduled_report_id: Optional[int] = None
    data: Optional[dict] = None

@router.post("/schedules")
def create_scheduled_report(report: ScheduledReportCreate, db: Session = Depends(get_db)):
    """Create a scheduled report"""
    result = ReportService.create_scheduled_report(
        db,
        template_id=report.template_id,
        name=report.name,
        schedule_cron=report.schedule_cron,
        recipients=report.recipients,
        config=report.config
    )
    return {
        "id": result.id,
        "name": result.name,
        "next_run": result.next_run.isoformat()
    }

@router.get("/schedules")
def get_scheduled_reports(db: Session = Depends(get_db)):
    """Get all scheduled reports"""
    from app.models.template import ScheduledReport
    reports = db.query(ScheduledReport).filter(ScheduledReport.is_active == True).all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "template_id": r.template_id,
            "schedule_cron": r.schedule_cron,
            "recipients": r.recipients,
            "last_run": r.last_run.isoformat() if r.last_run else None,
            "next_run": r.next_run.isoformat() if r.next_run else None
        }
        for r in reports
    ]

@router.post("/generate")
def generate_report(request: GenerateReportRequest, 
                   background_tasks: BackgroundTasks,
                   db: Session = Depends(get_db)):
    """Generate a report immediately"""
    if not request.scheduled_report_id:
        raise HTTPException(status_code=400, detail="scheduled_report_id required")
    
    try:
        execution = ReportService.generate_report(
            db,
            scheduled_report_id=request.scheduled_report_id,
            data=request.data
        )
        
        # Send emails in background
        from app.models.template import ScheduledReport
        scheduled_report = db.query(ScheduledReport).filter(
            ScheduledReport.id == request.scheduled_report_id
        ).first()
        
        if scheduled_report and scheduled_report.recipients:
            email_service = EmailService()
            background_tasks.add_task(
                email_service.send_report,
                db,
                execution.id,
                scheduled_report.recipients
            )
        
        return {
            "execution_id": execution.id,
            "status": execution.status.value,
            "output_file": execution.output_file
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/executions")
def get_executions(scheduled_report_id: Optional[int] = None, 
                  limit: int = 100,
                  db: Session = Depends(get_db)):
    """Get report executions"""
    executions = ReportService.get_executions(db, scheduled_report_id, limit=limit)
    return [
        {
            "id": e.id,
            "scheduled_report_id": e.scheduled_report_id,
            "status": e.status.value,
            "started_at": e.started_at.isoformat(),
            "completed_at": e.completed_at.isoformat() if e.completed_at else None,
            "execution_time": e.execution_time,
            "output_file": e.output_file,
            "error_message": e.error_message
        }
        for e in executions
    ]

@router.get("/executions/{execution_id}/download")
def download_report(execution_id: int, db: Session = Depends(get_db)):
    """Download generated report"""
    from app.models.template import ReportExecution
    execution = db.query(ReportExecution).filter(ReportExecution.id == execution_id).first()
    
    if not execution or not execution.output_file:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if not os.path.exists(execution.output_file):
        raise HTTPException(status_code=404, detail="Report file not found")
    
    return FileResponse(
        execution.output_file,
        filename=os.path.basename(execution.output_file)
    )
EOF

# Main FastAPI app
cat > backend/app/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import templates_router, reports_router
from app.database import init_db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Report Templates API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
@app.on_event("startup")
def startup():
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized")

# Include routers
app.include_router(templates_router)
app.include_router(reports_router)

@app.get("/")
def read_root():
    return {"message": "Report Templates API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
EOF

# Scheduler runner
cat > backend/scheduler.py << 'EOF'
from app.services.scheduler_service import SchedulerService
from app.database import init_db
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting scheduler service...")
    init_db()
    
    scheduler = SchedulerService()
    scheduler.start()
    
    logger.info("Scheduler running. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping scheduler...")
        scheduler.stop()
EOF

# Backend tests
cat > backend/tests/test_template_service.py << 'EOF'
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.template import Base, Template, ReportFormat
from app.services.template_service import TemplateService

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_create_template(db_session):
    template = TemplateService.create_template(
        db_session,
        name="Test Template",
        content="<h1>{{ title }}</h1>"
    )
    assert template.id is not None
    assert template.name == "Test Template"
    assert "title" in template.variables

def test_extract_variables():
    content = "Hello {{ name }}, today is {{ date }}"
    variables = TemplateService.extract_variables(content)
    assert "name" in variables
    assert "date" in variables

def test_validate_template():
    valid, msg = TemplateService.validate_template("<h1>{{ title }}</h1>")
    assert valid is True
    
    valid, msg = TemplateService.validate_template("<h1>{{ unclosed }</h1>")
    assert valid is False

def test_render_template(db_session):
    template = TemplateService.create_template(
        db_session,
        name="Test",
        content="<h1>{{ title }}</h1>"
    )
    rendered = TemplateService.render_template(template, {"title": "Hello World"})
    assert "Hello World" in rendered
EOF

# Frontend package.json
cat > frontend/package.json << 'EOF'
{
  "name": "report-templates-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.28.0",
    "@mui/material": "^6.1.7",
    "@mui/icons-material": "^6.1.7",
    "@emotion/react": "^11.13.5",
    "@emotion/styled": "^11.13.5",
    "@monaco-editor/react": "^4.6.0",
    "axios": "^1.7.8",
    "date-fns": "^4.1.0",
    "recharts": "^2.13.3",
    "cronstrue": "^2.51.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.4",
    "vite": "^6.0.1"
  },
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }
}
EOF

# Frontend vite config
cat > frontend/vite.config.js << 'EOF'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
EOF

# Frontend index.html
cat > frontend/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Report Templates System</title>
</head>
<body>
  <div id="root"></div>
  <script type="module" src="/src/main.jsx"></script>
</body>
</html>
EOF

# Frontend API service
cat > frontend/src/services/api.js << 'EOF'
import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

export const templateApi = {
  getAll: () => api.get('/templates'),
  getById: (id) => api.get(`/templates/${id}`),
  create: (data) => api.post('/templates', data),
  update: (id, data) => api.put(`/templates/${id}`, data),
  delete: (id) => api.delete(`/templates/${id}`),
  preview: (id, data) => api.post(`/templates/${id}/preview`, { data })
};

export const reportApi = {
  getSchedules: () => api.get('/reports/schedules'),
  createSchedule: (data) => api.post('/reports/schedules', data),
  generate: (data) => api.post('/reports/generate', data),
  getExecutions: (scheduledReportId) => 
    api.get('/reports/executions', { params: { scheduled_report_id: scheduledReportId } }),
  download: (executionId) => 
    api.get(`/reports/executions/${executionId}/download`, { responseType: 'blob' })
};

export default api;
EOF

# Frontend main component
cat > frontend/src/main.jsx << 'EOF'
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
EOF

cat > frontend/src/App.jsx << 'EOF'
import React, { useState } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box, AppBar, Toolbar, Typography, Drawer, List, ListItem, ListItemIcon, ListItemText, Container } from '@mui/material';
import { Description, Schedule, Assessment, Dashboard as DashboardIcon } from '@mui/icons-material';
import Dashboard from './pages/Dashboard';
import Templates from './pages/Templates';
import Schedules from './pages/Schedules';
import Executions from './pages/Executions';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#1976d2' },
    secondary: { main: '#dc004e' },
  },
});

const drawerWidth = 240;

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: <DashboardIcon /> },
    { id: 'templates', label: 'Templates', icon: <Description /> },
    { id: 'schedules', label: 'Schedules', icon: <Schedule /> },
    { id: 'executions', label: 'Executions', icon: <Assessment /> },
  ];

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard': return <Dashboard />;
      case 'templates': return <Templates />;
      case 'schedules': return <Schedules />;
      case 'executions': return <Executions />;
      default: return <Dashboard />;
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex' }}>
        <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
          <Toolbar>
            <Typography variant="h6" noWrap component="div">
              Report Templates System
            </Typography>
          </Toolbar>
        </AppBar>
        <Drawer
          variant="permanent"
          sx={{
            width: drawerWidth,
            flexShrink: 0,
            '& .MuiDrawer-paper': { width: drawerWidth, boxSizing: 'border-box' },
          }}
        >
          <Toolbar />
          <Box sx={{ overflow: 'auto', mt: 2 }}>
            <List>
              {menuItems.map((item) => (
                <ListItem
                  button
                  key={item.id}
                  selected={currentPage === item.id}
                  onClick={() => setCurrentPage(item.id)}
                >
                  <ListItemIcon>{item.icon}</ListItemIcon>
                  <ListItemText primary={item.label} />
                </ListItem>
              ))}
            </List>
          </Box>
        </Drawer>
        <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
          <Toolbar />
          <Container maxWidth="xl">
            {renderPage()}
          </Container>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;
EOF

cat > frontend/src/pages/Dashboard.jsx << 'EOF'
import React, { useEffect, useState } from 'react';
import { Grid, Paper, Typography, Box, Card, CardContent } from '@mui/material';
import { Assessment, Schedule, CheckCircle, Error } from '@mui/icons-material';
import { reportApi } from '../services/api';

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalSchedules: 0,
    activeSchedules: 0,
    completedReports: 0,
    failedReports: 0
  });

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const [schedules, executions] = await Promise.all([
        reportApi.getSchedules(),
        reportApi.getExecutions()
      ]);

      const completed = executions.data.filter(e => e.status === 'completed').length;
      const failed = executions.data.filter(e => e.status === 'failed').length;

      setStats({
        totalSchedules: schedules.data.length,
        activeSchedules: schedules.data.length,
        completedReports: completed,
        failedReports: failed
      });
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const StatCard = ({ title, value, icon, color }) => (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography color="textSecondary" gutterBottom>
              {title}
            </Typography>
            <Typography variant="h4">
              {value}
            </Typography>
          </Box>
          <Box sx={{ color: color }}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Schedules"
            value={stats.totalSchedules}
            icon={<Schedule sx={{ fontSize: 40 }} />}
            color="primary.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Schedules"
            value={stats.activeSchedules}
            icon={<Assessment sx={{ fontSize: 40 }} />}
            color="success.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md=3}>
          <StatCard
            title="Completed Reports"
            value={stats.completedReports}
            icon={<CheckCircle sx={{ fontSize: 40 }} />}
            color="info.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Failed Reports"
            value={stats.failedReports}
            icon={<Error sx={{ fontSize: 40 }} />}
            color="error.main"
          />
        </Grid>
      </Grid>
    </Box>
  );
}
EOF

cat > frontend/src/pages/Templates.jsx << 'EOF'
import React, { useEffect, useState } from 'react';
import { Box, Typography, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Dialog, DialogTitle, DialogContent, DialogActions, TextField } from '@mui/material';
import { Add } from '@mui/icons-material';
import { templateApi } from '../services/api';

export default function Templates() {
  const [templates, setTemplates] = useState([]);
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState({ name: '', description: '', content: '' });

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const response = await templateApi.getAll();
      setTemplates(response.data);
    } catch (error) {
      console.error('Failed to load templates:', error);
    }
  };

  const handleCreate = async () => {
    try {
      await templateApi.create(formData);
      setOpen(false);
      setFormData({ name: '', description: '', content: '' });
      loadTemplates();
    } catch (error) {
      console.error('Failed to create template:', error);
    }
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Templates</Typography>
        <Button variant="contained" startIcon={<Add />} onClick={() => setOpen(true)}>
          New Template
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Format</TableCell>
              <TableCell>Version</TableCell>
              <TableCell>Variables</TableCell>
              <TableCell>Created</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {templates.map((template) => (
              <TableRow key={template.id}>
                <TableCell>{template.name}</TableCell>
                <TableCell>{template.description}</TableCell>
                <TableCell>{template.format}</TableCell>
                <TableCell>v{template.version}</TableCell>
                <TableCell>{template.variables.join(', ')}</TableCell>
                <TableCell>{new Date(template.created_at).toLocaleDateString()}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create Template</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Description"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            margin="normal"
          />
          <TextField
            fullWidth
            multiline
            rows={10}
            label="Template Content"
            value={formData.content}
            onChange={(e) => setFormData({ ...formData, content: e.target.value })}
            margin="normal"
            placeholder="<h1>{{ title }}</h1>"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button onClick={handleCreate} variant="contained">Create</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
EOF

cat > frontend/src/pages/Schedules.jsx << 'EOF'
import React, { useEffect, useState } from 'react';
import { Box, Typography, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Dialog, DialogTitle, DialogContent, DialogActions, TextField, MenuItem } from '@mui/material';
import { Add, PlayArrow } from '@mui/icons-material';
import { reportApi, templateApi } from '../services/api';

export default function Schedules() {
  const [schedules, setSchedules] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    template_id: '',
    schedule_cron: '0 9 * * MON',
    recipients: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [schedulesRes, templatesRes] = await Promise.all([
        reportApi.getSchedules(),
        templateApi.getAll()
      ]);
      setSchedules(schedulesRes.data);
      setTemplates(templatesRes.data);
    } catch (error) {
      console.error('Failed to load data:', error);
    }
  };

  const handleCreate = async () => {
    try {
      const data = {
        ...formData,
        recipients: formData.recipients.split(',').map(s => s.trim())
      };
      await reportApi.createSchedule(data);
      setOpen(false);
      setFormData({ name: '', template_id: '', schedule_cron: '0 9 * * MON', recipients: '' });
      loadData();
    } catch (error) {
      console.error('Failed to create schedule:', error);
    }
  };

  const handleGenerate = async (scheduleId) => {
    try {
      await reportApi.generate({ scheduled_report_id: scheduleId });
      alert('Report generation started!');
    } catch (error) {
      console.error('Failed to generate report:', error);
    }
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Scheduled Reports</Typography>
        <Button variant="contained" startIcon={<Add />} onClick={() => setOpen(true)}>
          New Schedule
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Schedule</TableCell>
              <TableCell>Recipients</TableCell>
              <TableCell>Last Run</TableCell>
              <TableCell>Next Run</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {schedules.map((schedule) => (
              <TableRow key={schedule.id}>
                <TableCell>{schedule.name}</TableCell>
                <TableCell>{schedule.schedule_cron}</TableCell>
                <TableCell>{schedule.recipients.join(', ')}</TableCell>
                <TableCell>{schedule.last_run ? new Date(schedule.last_run).toLocaleString() : 'Never'}</TableCell>
                <TableCell>{schedule.next_run ? new Date(schedule.next_run).toLocaleString() : 'N/A'}</TableCell>
                <TableCell>
                  <Button
                    size="small"
                    startIcon={<PlayArrow />}
                    onClick={() => handleGenerate(schedule.id)}
                  >
                    Run Now
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create Scheduled Report</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            margin="normal"
          />
          <TextField
            fullWidth
            select
            label="Template"
            value={formData.template_id}
            onChange={(e) => setFormData({ ...formData, template_id: e.target.value })}
            margin="normal"
          >
            {templates.map((t) => (
              <MenuItem key={t.id} value={t.id}>{t.name}</MenuItem>
            ))}
          </TextField>
          <TextField
            fullWidth
            label="Schedule (Cron)"
            value={formData.schedule_cron}
            onChange={(e) => setFormData({ ...formData, schedule_cron: e.target.value })}
            margin="normal"
            helperText="e.g., '0 9 * * MON' for Mondays at 9am"
          />
          <TextField
            fullWidth
            label="Recipients (comma-separated)"
            value={formData.recipients}
            onChange={(e) => setFormData({ ...formData, recipients: e.target.value })}
            margin="normal"
            placeholder="user1@example.com, user2@example.com"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button onClick={handleCreate} variant="contained">Create</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
EOF

cat > frontend/src/pages/Executions.jsx << 'EOF'
import React, { useEffect, useState } from 'react';
import { Box, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Chip, IconButton } from '@mui/material';
import { Download } from '@mui/icons-material';
import { reportApi } from '../services/api';

export default function Executions() {
  const [executions, setExecutions] = useState([]);

  useEffect(() => {
    loadExecutions();
    const interval = setInterval(loadExecutions, 5000); // Refresh every 5s
    return () => clearInterval(interval);
  }, []);

  const loadExecutions = async () => {
    try {
      const response = await reportApi.getExecutions();
      setExecutions(response.data);
    } catch (error) {
      console.error('Failed to load executions:', error);
    }
  };

  const handleDownload = async (executionId) => {
    try {
      const response = await reportApi.download(executionId);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `report_${executionId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Failed to download report:', error);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      completed: 'success',
      processing: 'info',
      failed: 'error',
      pending: 'warning'
    };
    return colors[status] || 'default';
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Report Executions
      </Typography>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Started</TableCell>
              <TableCell>Completed</TableCell>
              <TableCell>Execution Time</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {executions.map((execution) => (
              <TableRow key={execution.id}>
                <TableCell>{execution.id}</TableCell>
                <TableCell>
                  <Chip
                    label={execution.status}
                    color={getStatusColor(execution.status)}
                    size="small"
                  />
                </TableCell>
                <TableCell>{new Date(execution.started_at).toLocaleString()}</TableCell>
                <TableCell>
                  {execution.completed_at ? new Date(execution.completed_at).toLocaleString() : '-'}
                </TableCell>
                <TableCell>{execution.execution_time ? `${execution.execution_time}s` : '-'}</TableCell>
                <TableCell>
                  {execution.status === 'completed' && (
                    <IconButton onClick={() => handleDownload(execution.id)} size="small">
                      <Download />
                    </IconButton>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}
EOF

# Sample template
cat > sample-templates/weekly_summary.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #1976d2; }
        .metric { background: #f5f5f5; padding: 20px; margin: 10px 0; border-radius: 8px; }
        .metric-value { font-size: 32px; font-weight: bold; color: #1976d2; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #1976d2; color: white; }
    </style>
</head>
<body>
    <h1>{{ company_name }} - {{ report_type }}</h1>
    <p>Report Period: {{ date_range }}</p>
    <p>Hello {{ recipient_name }},</p>
    
    <h2>Alert Summary</h2>
    <div class="metric">
        <div>Total Alerts</div>
        <div class="metric-value">{{ total_alerts }}</div>
    </div>
    
    {% if critical_alerts > 0 %}
    <div class="metric" style="background: #ffebee;">
        <div>⚠️ Critical Alerts</div>
        <div class="metric-value" style="color: #c62828;">{{ critical_alerts }}</div>
    </div>
    {% endif %}
    
    <h2>Top Services</h2>
    <table>
        <tr>
            <th>Service</th>
            <th>Alert Count</th>
            <th>Severity</th>
        </tr>
        {% for service in top_services %}
        <tr>
            <td>{{ service.name }}</td>
            <td>{{ service.count }}</td>
            <td>{{ service.severity }}</td>
        </tr>
        {% endfor %}
    </table>
    
    <h2>Performance Metrics</h2>
    <p>Average Response Time: {{ performance_metrics.avg_response_time }}</p>
    <p>Uptime: {{ performance_metrics.uptime }}</p>
    <p>Error Rate: {{ performance_metrics.error_rate }}</p>
</body>
</html>
EOF

# Docker Compose
cat > docker/docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: reports_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports:
      - "6379:6379"

volumes:
  postgres_data:
EOF

# Build script
cat > build.sh << 'EOF'
#!/bin/bash

echo "=========================================="
echo "Building Report Templates System"
echo "=========================================="

# Check if Docker is requested
USE_DOCKER=${1:-"local"}

if [ "$USE_DOCKER" = "docker" ]; then
    echo "Starting services with Docker..."
    cd docker
    docker-compose up -d
    cd ..
    sleep 5
else
    echo "Setting up local environment..."
    
    # Start PostgreSQL
    echo "Starting PostgreSQL..."
    docker run -d --name reports-postgres \
        -e POSTGRES_PASSWORD=postgres \
        -e POSTGRES_DB=reports_db \
        -p 5432:5432 \
        postgres:15
    
    # Start Redis
    echo "Starting Redis..."
    docker run -d --name reports-redis \
        -p 6379:6379 \
        redis:7
    
    sleep 5
fi

# Backend setup
echo "Setting up backend..."
cd backend

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

# Initialize database
echo "Initializing database..."
python -c "from app.database import init_db; init_db()"

# Run tests
echo "Running tests..."
pytest tests/ -v

# Start backend services
echo "Starting API server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!

echo "Starting scheduler..."
python scheduler.py &
SCHEDULER_PID=$!

cd ..

# Frontend setup
echo "Setting up frontend..."
cd frontend

npm install

echo "Starting frontend..."
npm run dev &
FRONTEND_PID=$!

cd ..

# Save PIDs
echo $API_PID > .api.pid
echo $SCHEDULER_PID > .scheduler.pid
echo $FRONTEND_PID > .frontend.pid

echo ""
echo "=========================================="
echo "Build Complete!"
echo "=========================================="
echo "API Server: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Run ./stop.sh to stop all services"
EOF

chmod +x build.sh

# Stop script
cat > stop.sh << 'EOF'
#!/bin/bash

echo "Stopping Report Templates System..."

# Kill backend processes
if [ -f .api.pid ]; then
    kill $(cat .api.pid) 2>/dev/null
    rm .api.pid
fi

if [ -f .scheduler.pid ]; then
    kill $(cat .scheduler.pid) 2>/dev/null
    rm .scheduler.pid
fi

if [ -f .frontend.pid ]; then
    kill $(cat .frontend.pid) 2>/dev/null
    rm .frontend.pid
fi

# Stop Docker containers
docker stop reports-postgres reports-redis 2>/dev/null
docker rm reports-postgres reports-redis 2>/dev/null

# Stop docker-compose if used
cd docker 2>/dev/null && docker-compose down 2>/dev/null

echo "All services stopped"
EOF

chmod +x stop.sh

# Demo script
cat > demo.sh << 'EOF'
#!/bin/bash

echo "=========================================="
echo "Report Templates System Demo"
echo "=========================================="

API_URL="http://localhost:8000"

echo "1. Creating template..."
TEMPLATE_ID=$(curl -s -X POST "$API_URL/api/templates" \
  -H "Content-Type: application/json" \
  -d @sample-templates/weekly_summary.json | jq -r '.id')
echo "Template created with ID: $TEMPLATE_ID"

echo "2. Creating scheduled report..."
SCHEDULE_ID=$(curl -s -X POST "$API_URL/api/reports/schedules" \
  -H "Content-Type: application/json" \
  -d "{
    \"template_id\": $TEMPLATE_ID,
    \"name\": \"Weekly Summary Report\",
    \"schedule_cron\": \"0 9 * * MON\",
    \"recipients\": [\"team@example.com\"]
  }" | jq -r '.id')
echo "Schedule created with ID: $SCHEDULE_ID"

echo "3. Generating report..."
EXECUTION_ID=$(curl -s -X POST "$API_URL/api/reports/generate" \
  -H "Content-Type: application/json" \
  -d "{
    \"scheduled_report_id\": $SCHEDULE_ID
  }" | jq -r '.execution_id')
echo "Report execution ID: $EXECUTION_ID"

echo ""
echo "Demo complete! Check:"
echo "- Frontend: http://localhost:3000"
echo "- API Docs: http://localhost:8000/docs"
EOF

chmod +x demo.sh

# Sample template JSON
cat > sample-templates/weekly_summary.json << 'EOF'
{
  "name": "Weekly Summary Report",
  "description": "Weekly alert and performance summary",
  "content": "<!DOCTYPE html>\n<html>\n<head>\n    <style>\n        body { font-family: Arial, sans-serif; margin: 40px; }\n        h1 { color: #1976d2; }\n    </style>\n</head>\n<body>\n    <h1>{{ company_name }} - {{ report_type }}</h1>\n    <p>Report Period: {{ date_range }}</p>\n    <p>Total Alerts: {{ total_alerts }}</p>\n</body>\n</html>",
  "format": "html"
}
EOF

# README
cat > README.md << 'EOF'
# Report Templates System

Production-ready report template system with dynamic generation, scheduling, and email delivery.

## Features
- Template management with version control
- Dynamic report generation with Jinja2
- Scheduled reports with cron expressions
- Email delivery with SendGrid
- HTML and PDF output formats
- Real-time execution tracking

## Quick Start

### Local Development
```bash
./build.sh local
```

### With Docker
```bash
./build.sh docker
```

### Access Points
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Running Demo
```bash
./demo.sh
```

## Testing
```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

## Stop Services
```bash
./stop.sh
```
EOF

echo "=========================================="
echo "Project Created Successfully!"
echo "=========================================="
echo "Location: $PROJECT_NAME"
echo ""
echo "To build and run:"
echo "  cd $PROJECT_NAME"
echo "  ./build.sh          # Local development"
echo "  ./build.sh docker   # With Docker"
echo ""
echo "To run demo:"
echo "  ./demo.sh"
echo ""
echo "To stop:"
echo "  ./stop.sh"

chmod +x build.sh stop.sh demo.sh

echo "=========================================="
echo "Project Created Successfully!"
echo "=========================================="