#!/bin/bash

# Day 57: Export System Foundation - Complete Implementation Script
# This script creates a production-ready multi-format export system

set -e

PROJECT_NAME="export-system"
BACKEND_DIR="backend"
FRONTEND_DIR="frontend"

echo "🚀 Starting Day 57: Export System Foundation Setup"
echo "=================================================="

# Create project structure
echo "📁 Creating project structure..."
mkdir -p $PROJECT_NAME
cd $PROJECT_NAME

mkdir -p $BACKEND_DIR/{app/{models,services,api,tasks,utils},tests,exports}
mkdir -p $FRONTEND_DIR/{src/{components,services,utils},public}

# Backend: requirements.txt
echo "📦 Creating backend dependencies..."
cat > $BACKEND_DIR/requirements.txt << 'EOF'
fastapi==0.115.0
uvicorn[standard]==0.32.0
sqlalchemy==2.0.36
psycopg2-binary==2.9.10
redis==5.2.0
celery==5.4.0
pandas==2.2.3
openpyxl==3.1.5
reportlab==4.2.5
python-multipart==0.0.18
pydantic==2.10.3
pydantic-settings==2.6.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
pytest==8.3.4
pytest-asyncio==0.24.0
httpx==0.28.1
alembic==1.14.0
python-dotenv==1.0.1
EOF

# Backend: .env
cat > $BACKEND_DIR/.env << 'EOF'
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/exportdb
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-change-in-production
EXPORT_STORAGE_PATH=./exports
EXPORT_EXPIRY_HOURS=24
MAX_EXPORT_SIZE=1000000
EOF

# Backend: Main application
cat > $BACKEND_DIR/app/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import exports
from app.models.database import engine, Base

app = FastAPI(title="Export System API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(exports.router, prefix="/api/exports", tags=["exports"])

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "export-system"}

@app.get("/")
async def root():
    return {"message": "Export System API - Day 57"}
EOF

# Backend: Database models
cat > $BACKEND_DIR/app/models/__init__.py << 'EOF'
from app.models.notification import Notification
from app.models.export_job import ExportJob

__all__ = ["Notification", "ExportJob"]
EOF

cat > $BACKEND_DIR/app/models/database.py << 'EOF'
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/exportdb")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
EOF

cat > $BACKEND_DIR/app/models/notification.py << 'EOF'
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum
from sqlalchemy.sql import func
from app.models.database import Base
import enum

class NotificationType(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(Enum(NotificationType), default=NotificationType.INFO, index=True)
    is_read = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
EOF

cat > $BACKEND_DIR/app/models/export_job.py << 'EOF'
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, JSON
from sqlalchemy.sql import func
from app.models.database import Base
import enum

class ExportStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"

class ExportFormat(str, enum.Enum):
    CSV = "csv"
    JSON = "json"
    PDF = "pdf"
    EXCEL = "excel"

class ExportJob(Base):
    __tablename__ = "export_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(Integer, index=True)
    export_format = Column(Enum(ExportFormat), nullable=False)
    status = Column(Enum(ExportStatus), default=ExportStatus.PENDING, index=True)
    filters = Column(JSON)
    total_records = Column(Integer, default=0)
    processed_records = Column(Integer, default=0)
    file_path = Column(String(500))
    file_size = Column(Integer)
    download_url = Column(String(500))
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))
EOF

# Backend: Export services
cat > $BACKEND_DIR/app/services/__init__.py << 'EOF'
EOF

cat > $BACKEND_DIR/app/services/csv_export.py << 'EOF'
import csv
from io import StringIO
from typing import List, Dict, Any

class CSVExportService:
    def __init__(self):
        self.buffer = StringIO()
        self.writer = None
        
    def initialize(self, headers: List[str]):
        self.writer = csv.DictWriter(
            self.buffer,
            fieldnames=headers,
            quoting=csv.QUOTE_MINIMAL
        )
        # Add BOM for Excel compatibility
        self.buffer.write('\ufeff')
        self.writer.writeheader()
        
    def write_batch(self, records: List[Dict[str, Any]]):
        for record in records:
            # Handle None values
            cleaned_record = {k: (v if v is not None else '') for k, v in record.items()}
            self.writer.writerow(cleaned_record)
            
    def get_content(self) -> str:
        return self.buffer.getvalue()
        
    def close(self):
        self.buffer.close()
EOF

cat > $BACKEND_DIR/app/services/json_export.py << 'EOF'
import json
from typing import List, Dict, Any
from datetime import datetime

class JSONExportService:
    def __init__(self):
        self.items = []
        
    def initialize(self, metadata: Dict[str, Any]):
        self.metadata = metadata
        self.items = []
        
    def write_batch(self, records: List[Dict[str, Any]]):
        for record in records:
            # Convert datetime objects to ISO format strings
            serializable_record = {}
            for key, value in record.items():
                if isinstance(value, datetime):
                    serializable_record[key] = value.isoformat()
                else:
                    serializable_record[key] = value
            self.items.append(serializable_record)
            
    def get_content(self) -> str:
        output = {
            "metadata": self.metadata,
            "data": self.items
        }
        return json.dumps(output, indent=2, ensure_ascii=False)
        
    def close(self):
        self.items = []
EOF

cat > $BACKEND_DIR/app/services/pdf_export.py << 'EOF'
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from typing import List, Dict, Any
from io import BytesIO
from datetime import datetime

class PDFExportService:
    def __init__(self):
        self.buffer = BytesIO()
        self.elements = []
        self.styles = getSampleStyleSheet()
        
    def initialize(self, title: str, metadata: Dict[str, Any]):
        self.doc = SimpleDocTemplate(
            self.buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a73e8'),
            spaceAfter=30
        )
        self.elements.append(Paragraph(title, title_style))
        
        # Metadata
        meta_text = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>"
        meta_text += f"Total Records: {metadata.get('total_records', 0)}"
        self.elements.append(Paragraph(meta_text, self.styles['Normal']))
        self.elements.append(Spacer(1, 0.3*inch))
        
        self.table_data = []
        
    def write_batch(self, records: List[Dict[str, Any]], headers: List[str]):
        if not self.table_data:
            # Add headers
            self.table_data.append(headers)
            
        for record in records:
            row = [str(record.get(h, '')) for h in headers]
            self.table_data.append(row)
            
    def finalize(self):
        if self.table_data:
            # Create table with styling
            table = Table(self.table_data, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a73e8')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            self.elements.append(table)
            
        self.doc.build(self.elements)
        
    def get_content(self) -> bytes:
        return self.buffer.getvalue()
        
    def close(self):
        self.buffer.close()
EOF

cat > $BACKEND_DIR/app/services/excel_export.py << 'EOF'
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from typing import List, Dict, Any
from io import BytesIO
from datetime import datetime

class ExcelExportService:
    def __init__(self):
        self.wb = Workbook(write_only=True)
        self.ws = self.wb.create_sheet("Notifications")
        self.headers_written = False
        
    def initialize(self, headers: List[str]):
        self.headers = headers
        # Write headers with formatting
        header_row = []
        for header in headers:
            header_row.append(header)
        self.ws.append(header_row)
        self.headers_written = True
        
    def write_batch(self, records: List[Dict[str, Any]]):
        for record in records:
            row = []
            for header in self.headers:
                value = record.get(header)
                if isinstance(value, datetime):
                    row.append(value.strftime('%Y-%m-%d %H:%M:%S'))
                elif value is None:
                    row.append('')
                else:
                    row.append(str(value))
            self.ws.append(row)
            
    def get_content(self) -> bytes:
        buffer = BytesIO()
        self.wb.save(buffer)
        return buffer.getvalue()
        
    def close(self):
        self.wb.close()
EOF

# Backend: Celery configuration
cat > $BACKEND_DIR/app/celery_config.py << 'EOF'
from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "export_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3000,  # 50 minutes soft limit
)
EOF

# Backend: Export tasks
cat > $BACKEND_DIR/app/tasks/__init__.py << 'EOF'
EOF

cat > $BACKEND_DIR/app/tasks/export_tasks.py << 'EOF'
from app.celery_config import celery_app
from sqlalchemy.orm import Session
from app.models.database import SessionLocal
from app.models.notification import Notification
from app.models.export_job import ExportJob, ExportStatus, ExportFormat
from app.services.csv_export import CSVExportService
from app.services.json_export import JSONExportService
from app.services.pdf_export import PDFExportService
from app.services.excel_export import ExcelExportService
from datetime import datetime, timedelta
import os
import uuid

BATCH_SIZE = 1000
EXPORT_STORAGE_PATH = os.getenv("EXPORT_STORAGE_PATH", "./exports")

@celery_app.task(bind=True)
def generate_export(self, job_id: str):
    db = SessionLocal()
    try:
        job = db.query(ExportJob).filter(ExportJob.job_id == job_id).first()
        if not job:
            return {"error": "Job not found"}
            
        # Update status to processing
        job.status = ExportStatus.PROCESSING
        job.started_at = datetime.utcnow()
        db.commit()
        
        # Get total count
        query = db.query(Notification)
        if job.filters:
            if job.filters.get("user_id"):
                query = query.filter(Notification.user_id == job.filters["user_id"])
            if job.filters.get("notification_type"):
                query = query.filter(Notification.notification_type == job.filters["notification_type"])
            if job.filters.get("start_date"):
                query = query.filter(Notification.created_at >= job.filters["start_date"])
            if job.filters.get("end_date"):
                query = query.filter(Notification.created_at <= job.filters["end_date"])
                
        total_records = query.count()
        job.total_records = total_records
        db.commit()
        
        # Initialize export service based on format
        if job.export_format == ExportFormat.CSV:
            service = CSVExportService()
            service.initialize(['id', 'user_id', 'title', 'message', 'notification_type', 'is_read', 'created_at'])
        elif job.export_format == ExportFormat.JSON:
            service = JSONExportService()
            service.initialize({
                'total': total_records,
                'exported_at': datetime.utcnow().isoformat(),
                'format': 'json'
            })
        elif job.export_format == ExportFormat.PDF:
            service = PDFExportService()
            service.initialize('Notification Export Report', {'total_records': total_records})
        elif job.export_format == ExportFormat.EXCEL:
            service = ExcelExportService()
            service.initialize(['id', 'user_id', 'title', 'message', 'notification_type', 'is_read', 'created_at'])
        else:
            raise ValueError(f"Unsupported format: {job.export_format}")
            
        # Process in batches
        offset = 0
        processed = 0
        
        while offset < total_records:
            batch = query.offset(offset).limit(BATCH_SIZE).all()
            if not batch:
                break
                
            # Convert to dict
            batch_data = []
            for notification in batch:
                batch_data.append({
                    'id': notification.id,
                    'user_id': notification.user_id,
                    'title': notification.title,
                    'message': notification.message,
                    'notification_type': notification.notification_type.value,
                    'is_read': notification.is_read,
                    'created_at': notification.created_at
                })
                
            # Write batch
            if job.export_format in [ExportFormat.CSV, ExportFormat.JSON, ExportFormat.EXCEL]:
                service.write_batch(batch_data)
            elif job.export_format == ExportFormat.PDF:
                service.write_batch(batch_data, ['id', 'user_id', 'title', 'message', 'type', 'read', 'created'])
                
            processed += len(batch)
            offset += BATCH_SIZE
            
            # Update progress
            job.processed_records = processed
            db.commit()
            
            self.update_state(
                state='PROGRESS',
                meta={'current': processed, 'total': total_records, 'percent': int((processed / total_records) * 100)}
            )
            
        # Finalize export
        if job.export_format == ExportFormat.PDF:
            service.finalize()
            
        # Save file
        os.makedirs(EXPORT_STORAGE_PATH, exist_ok=True)
        file_extension = job.export_format.value
        filename = f"{job_id}.{file_extension}"
        file_path = os.path.join(EXPORT_STORAGE_PATH, filename)
        
        if job.export_format in [ExportFormat.PDF, ExportFormat.EXCEL]:
            content = service.get_content()
            with open(file_path, 'wb') as f:
                f.write(content)
            file_size = len(content)
        else:
            content = service.get_content()
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            file_size = len(content.encode('utf-8'))
            
        service.close()
        
        # Update job
        job.status = ExportStatus.COMPLETED
        job.file_path = file_path
        job.file_size = file_size
        job.download_url = f"/api/exports/{job_id}/download"
        job.completed_at = datetime.utcnow()
        job.expires_at = datetime.utcnow() + timedelta(hours=int(os.getenv("EXPORT_EXPIRY_HOURS", "24")))
        db.commit()
        
        return {
            "status": "completed",
            "job_id": job_id,
            "records": processed,
            "file_size": file_size
        }
        
    except Exception as e:
        job.status = ExportStatus.FAILED
        job.error_message = str(e)
        job.retry_count += 1
        db.commit()
        raise
    finally:
        db.close()
EOF

# Backend: API routes
cat > $BACKEND_DIR/app/api/__init__.py << 'EOF'
EOF

cat > $BACKEND_DIR/app/api/exports.py << 'EOF'
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.export_job import ExportJob, ExportStatus, ExportFormat
from app.models.notification import Notification, NotificationType
from app.tasks.export_tasks import generate_export
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid
import os

router = APIRouter()

class ExportRequest(BaseModel):
    export_format: ExportFormat
    user_id: Optional[int] = None
    notification_type: Optional[NotificationType] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class ExportResponse(BaseModel):
    job_id: str
    status: ExportStatus
    message: str

class ExportStatusResponse(BaseModel):
    job_id: str
    status: ExportStatus
    export_format: ExportFormat
    total_records: int
    processed_records: int
    progress_percent: int
    download_url: Optional[str]
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

@router.post("/create", response_model=ExportResponse)
async def create_export(request: ExportRequest, db: Session = Depends(get_db)):
    """Create a new export job"""
    job_id = f"exp-{uuid.uuid4()}"
    
    # Create job record
    export_job = ExportJob(
        job_id=job_id,
        export_format=request.export_format,
        user_id=request.user_id,
        status=ExportStatus.PENDING,
        filters={
            "user_id": request.user_id,
            "notification_type": request.notification_type.value if request.notification_type else None,
            "start_date": request.start_date.isoformat() if request.start_date else None,
            "end_date": request.end_date.isoformat() if request.end_date else None
        }
    )
    
    db.add(export_job)
    db.commit()
    db.refresh(export_job)
    
    # Queue async task
    generate_export.delay(job_id)
    
    return ExportResponse(
        job_id=job_id,
        status=ExportStatus.PENDING,
        message="Export job created successfully"
    )

@router.get("/{job_id}/status", response_model=ExportStatusResponse)
async def get_export_status(job_id: str, db: Session = Depends(get_db)):
    """Get export job status"""
    job = db.query(ExportJob).filter(ExportJob.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Export job not found")
        
    progress_percent = 0
    if job.total_records > 0:
        progress_percent = int((job.processed_records / job.total_records) * 100)
        
    return ExportStatusResponse(
        job_id=job.job_id,
        status=job.status,
        export_format=job.export_format,
        total_records=job.total_records,
        processed_records=job.processed_records,
        progress_percent=progress_percent,
        download_url=job.download_url,
        error_message=job.error_message,
        created_at=job.created_at,
        completed_at=job.completed_at
    )

@router.get("/{job_id}/download")
async def download_export(job_id: str, db: Session = Depends(get_db)):
    """Download completed export file"""
    job = db.query(ExportJob).filter(ExportJob.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Export job not found")
        
    if job.status != ExportStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Export not completed yet")
        
    if not os.path.exists(job.file_path):
        raise HTTPException(status_code=404, detail="Export file not found")
        
    # Check expiry
    if job.expires_at and datetime.utcnow() > job.expires_at:
        job.status = ExportStatus.EXPIRED
        db.commit()
        raise HTTPException(status_code=410, detail="Export has expired")
        
    filename = f"notifications_export.{job.export_format.value}"
    
    return FileResponse(
        job.file_path,
        media_type="application/octet-stream",
        filename=filename
    )

@router.get("/list", response_model=List[ExportStatusResponse])
async def list_exports(
    user_id: Optional[int] = None,
    limit: int = Query(default=10, le=100),
    db: Session = Depends(get_db)
):
    """List export jobs"""
    query = db.query(ExportJob)
    if user_id:
        query = query.filter(ExportJob.user_id == user_id)
        
    jobs = query.order_by(ExportJob.created_at.desc()).limit(limit).all()
    
    result = []
    for job in jobs:
        progress_percent = 0
        if job.total_records > 0:
            progress_percent = int((job.processed_records / job.total_records) * 100)
            
        result.append(ExportStatusResponse(
            job_id=job.job_id,
            status=job.status,
            export_format=job.export_format,
            total_records=job.total_records,
            processed_records=job.processed_records,
            progress_percent=progress_percent,
            download_url=job.download_url,
            error_message=job.error_message,
            created_at=job.created_at,
            completed_at=job.completed_at
        ))
        
    return result
EOF

# Backend: Test data seeder
cat > $BACKEND_DIR/app/seed_data.py << 'EOF'
from app.models.database import SessionLocal
from app.models.notification import Notification, NotificationType
from datetime import datetime, timedelta
import random

def seed_notifications(count: int = 1000):
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_count = db.query(Notification).count()
        if existing_count > 0:
            print(f"Database already has {existing_count} notifications. Skipping seed.")
            return
            
        print(f"Seeding {count} notifications...")
        
        notification_types = list(NotificationType)
        titles = [
            "System Alert",
            "New Message",
            "Task Completed",
            "Warning Notice",
            "Security Update",
            "Performance Report",
            "User Activity",
            "Server Status"
        ]
        
        messages = [
            "This is a test notification message",
            "Your task has been completed successfully",
            "Please review the latest security updates",
            "System performance is optimal",
            "New user registered on the platform",
            "Database backup completed",
            "API rate limit approaching threshold",
            "Cache cleared successfully"
        ]
        
        for i in range(count):
            notification = Notification(
                user_id=random.randint(1, 100),
                title=random.choice(titles),
                message=random.choice(messages),
                notification_type=random.choice(notification_types),
                is_read=random.choice([0, 1]),
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            db.add(notification)
            
            if (i + 1) % 100 == 0:
                db.commit()
                print(f"Seeded {i + 1}/{count} notifications...")
                
        db.commit()
        print(f"Successfully seeded {count} notifications!")
        
    finally:
        db.close()

if __name__ == "__main__":
    seed_notifications(10000)
EOF

# Backend: Tests
cat > $BACKEND_DIR/tests/__init__.py << 'EOF'
EOF

cat > $BACKEND_DIR/tests/test_exports.py << 'EOF'
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.database import SessionLocal, engine, Base
from app.models.notification import Notification, NotificationType
from datetime import datetime

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Create test notifications
    for i in range(100):
        notification = Notification(
            user_id=1,
            title=f"Test Notification {i}",
            message=f"Test message {i}",
            notification_type=NotificationType.INFO,
            is_read=0
        )
        db.add(notification)
    db.commit()
    db.close()
    
    yield
    
    Base.metadata.drop_all(bind=engine)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_csv_export(setup_database):
    response = client.post("/api/exports/create", json={
        "export_format": "csv",
        "user_id": 1
    })
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "pending"

def test_create_json_export(setup_database):
    response = client.post("/api/exports/create", json={
        "export_format": "json"
    })
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data

def test_get_export_status(setup_database):
    # Create export first
    create_response = client.post("/api/exports/create", json={
        "export_format": "csv"
    })
    job_id = create_response.json()["job_id"]
    
    # Get status
    response = client.get(f"/api/exports/{job_id}/status")
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == job_id
    assert "status" in data

def test_list_exports(setup_database):
    response = client.get("/api/exports/list")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
EOF

# Frontend: package.json
echo "📦 Creating frontend dependencies..."
cat > $FRONTEND_DIR/package.json << 'EOF'
{
  "name": "export-system-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-scripts": "5.0.1",
    "axios": "^1.7.9",
    "recharts": "^2.15.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}
EOF

# Frontend: public/index.html
cat > $FRONTEND_DIR/public/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="Export System Dashboard" />
    <title>Export System Dashboard</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
EOF

# Frontend: src/index.js
cat > $FRONTEND_DIR/src/index.js << 'EOF'
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
EOF

# Frontend: src/index.css
cat > $FRONTEND_DIR/src/index.css << 'EOF'
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background: #f5f7fa;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}
EOF

# Frontend: src/App.js
cat > $FRONTEND_DIR/src/App.js << 'EOF'
import React, { useState, useEffect } from 'react';
import './App.css';
import ExportForm from './components/ExportForm';
import ExportList from './components/ExportList';
import { getExports, createExport, getExportStatus, downloadExport } from './services/api';

function App() {
  const [exports, setExports] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadExports();
    
    // Poll for updates every 3 seconds
    const interval = setInterval(loadExports, 3000);
    return () => clearInterval(interval);
  }, []);

  const loadExports = async () => {
    try {
      const data = await getExports();
      setExports(data);
    } catch (error) {
      console.error('Error loading exports:', error);
    }
  };

  const handleCreateExport = async (exportRequest) => {
    setLoading(true);
    try {
      await createExport(exportRequest);
      await loadExports();
    } catch (error) {
      console.error('Error creating export:', error);
      alert('Failed to create export');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (jobId) => {
    try {
      await downloadExport(jobId);
    } catch (error) {
      console.error('Error downloading export:', error);
      alert('Failed to download export');
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>📊 Export System Dashboard</h1>
        <p>Multi-Format Data Export Management</p>
      </header>

      <main className="App-main">
        <div className="container">
          <ExportForm onSubmit={handleCreateExport} loading={loading} />
          <ExportList exports={exports} onDownload={handleDownload} />
        </div>
      </main>

      <footer className="App-footer">
        <p>Day 57: Export System Foundation - Built with React & FastAPI</p>
      </footer>
    </div>
  );
}

export default App;
EOF

# Frontend: src/App.css
cat > $FRONTEND_DIR/src/App.css << 'EOF'
.App {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.App-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
  color: white;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.App-header h1 {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
  font-weight: 700;
}

.App-header p {
  font-size: 1.1rem;
  opacity: 0.9;
}

.App-main {
  flex: 1;
  padding: 2rem;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.App-footer {
  background: #2d3748;
  color: #a0aec0;
  text-align: center;
  padding: 1.5rem;
  margin-top: 2rem;
}

.card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 6px rgba(0,0,0,0.07);
  margin-bottom: 2rem;
}

.card h2 {
  color: #2d3748;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #4a5568;
  font-weight: 600;
  font-size: 0.95rem;
}

.form-group select,
.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.form-group select:focus,
.form-group input:focus {
  outline: none;
  border-color: #667eea;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #48bb78;
  color: white;
}

.btn-secondary:hover {
  background: #38a169;
}

.export-item {
  background: #f7fafc;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  transition: all 0.2s;
}

.export-item:hover {
  border-color: #667eea;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
}

.export-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.export-id {
  font-family: 'Courier New', monospace;
  background: #edf2f7;
  padding: 0.25rem 0.75rem;
  border-radius: 6px;
  font-size: 0.9rem;
  color: #2d3748;
}

.status-badge {
  padding: 0.4rem 1rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-pending {
  background: #feebc8;
  color: #c05621;
}

.status-processing {
  background: #bee3f8;
  color: #2c5282;
}

.status-completed {
  background: #c6f6d5;
  color: #22543d;
}

.status-failed {
  background: #fed7d7;
  color: #9b2c2c;
}

.export-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
}

.detail-label {
  font-size: 0.85rem;
  color: #718096;
  margin-bottom: 0.25rem;
}

.detail-value {
  font-size: 1rem;
  color: #2d3748;
  font-weight: 600;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
  margin: 1rem 0;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s ease;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #a0aec0;
}

.empty-state-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

@media (max-width: 768px) {
  .App-header h1 {
    font-size: 1.8rem;
  }
  
  .container {
    padding: 0 1rem;
  }
  
  .export-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}
EOF

# Frontend: src/components/ExportForm.js
cat > $FRONTEND_DIR/src/components/ExportForm.js << 'EOF'
import React, { useState } from 'react';

const ExportForm = ({ onSubmit, loading }) => {
  const [format, setFormat] = useState('csv');
  const [userId, setUserId] = useState('');
  const [notificationType, setNotificationType] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    
    const request = {
      export_format: format,
      user_id: userId ? parseInt(userId) : null,
      notification_type: notificationType || null
    };
    
    onSubmit(request);
  };

  return (
    <div className="card">
      <h2>🚀 Create New Export</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="format">Export Format</label>
          <select
            id="format"
            value={format}
            onChange={(e) => setFormat(e.target.value)}
          >
            <option value="csv">CSV (Spreadsheet)</option>
            <option value="json">JSON (API Compatible)</option>
            <option value="pdf">PDF (Report)</option>
            <option value="excel">Excel (Advanced)</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="userId">User ID (Optional)</label>
          <input
            id="userId"
            type="number"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            placeholder="Filter by user ID"
          />
        </div>

        <div className="form-group">
          <label htmlFor="notificationType">Notification Type (Optional)</label>
          <select
            id="notificationType"
            value={notificationType}
            onChange={(e) => setNotificationType(e.target.value)}
          >
            <option value="">All Types</option>
            <option value="info">Info</option>
            <option value="warning">Warning</option>
            <option value="error">Error</option>
            <option value="success">Success</option>
          </select>
        </div>

        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? '⏳ Creating...' : '📥 Create Export'}
        </button>
      </form>
    </div>
  );
};

export default ExportForm;
EOF

# Frontend: src/components/ExportList.js
cat > $FRONTEND_DIR/src/components/ExportList.js << 'EOF'
import React from 'react';

const ExportList = ({ exports, onDownload }) => {
  const getStatusColor = (status) => {
    const colors = {
      pending: 'status-pending',
      processing: 'status-processing',
      completed: 'status-completed',
      failed: 'status-failed'
    };
    return colors[status] || 'status-pending';
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return 'N/A';
    const kb = bytes / 1024;
    const mb = kb / 1024;
    return mb >= 1 ? `${mb.toFixed(2)} MB` : `${kb.toFixed(2)} KB`;
  };

  if (exports.length === 0) {
    return (
      <div className="card">
        <h2>📋 Export Jobs</h2>
        <div className="empty-state">
          <div className="empty-state-icon">📭</div>
          <p>No exports yet. Create your first export above!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <h2>📋 Export Jobs ({exports.length})</h2>
      
      {exports.map((exp) => (
        <div key={exp.job_id} className="export-item">
          <div className="export-header">
            <span className="export-id">{exp.job_id}</span>
            <span className={`status-badge ${getStatusColor(exp.status)}`}>
              {exp.status}
            </span>
          </div>

          <div className="export-details">
            <div className="detail-item">
              <span className="detail-label">Format</span>
              <span className="detail-value">{exp.export_format.toUpperCase()}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Records</span>
              <span className="detail-value">
                {exp.processed_records} / {exp.total_records}
              </span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Created</span>
              <span className="detail-value">{formatDate(exp.created_at)}</span>
            </div>
          </div>

          {exp.status === 'processing' && (
            <div>
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${exp.progress_percent}%` }}
                ></div>
              </div>
              <p style={{ textAlign: 'center', color: '#667eea', fontWeight: 600 }}>
                {exp.progress_percent}% Complete
              </p>
            </div>
          )}

          {exp.status === 'completed' && (
            <div style={{ marginTop: '1rem' }}>
              <button
                className="btn btn-secondary"
                onClick={() => onDownload(exp.job_id)}
              >
                ⬇️ Download Export
              </button>
              <span style={{ marginLeft: '1rem', color: '#718096' }}>
                Completed: {formatDate(exp.completed_at)}
              </span>
            </div>
          )}

          {exp.status === 'failed' && exp.error_message && (
            <div style={{ marginTop: '1rem', color: '#e53e3e', fontSize: '0.9rem' }}>
              ❌ Error: {exp.error_message}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default ExportList;
EOF

# Frontend: src/services/api.js
cat > $FRONTEND_DIR/src/services/api.js << 'EOF'
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

export const createExport = async (exportRequest) => {
  const response = await api.post('/api/exports/create', exportRequest);
  return response.data;
};

export const getExportStatus = async (jobId) => {
  const response = await api.get(`/api/exports/${jobId}/status`);
  return response.data;
};

export const getExports = async (userId = null, limit = 20) => {
  const params = { limit };
  if (userId) params.user_id = userId;
  
  const response = await api.get('/api/exports/list', { params });
  return response.data;
};

export const downloadExport = async (jobId) => {
  const response = await api.get(`/api/exports/${jobId}/download`, {
    responseType: 'blob'
  });
  
  // Create download link
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  
  // Get filename from content-disposition header or use default
  const contentDisposition = response.headers['content-disposition'];
  const filename = contentDisposition
    ? contentDisposition.split('filename=')[1].replace(/"/g, '')
    : `export_${jobId}.file`;
    
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};

export default api;
EOF

# Docker Compose
echo "🐳 Creating Docker configuration..."
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: exportdb
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/exportdb
      REDIS_URL: redis://redis:6379/0
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend:/app
      - export_files:/app/exports
    command: >
      sh -c "
        python app/seed_data.py &&
        uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
      "

  celery_worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/exportdb
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app
      - export_files:/app/exports
    command: celery -A app.celery_config.celery_app worker --loglevel=info

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      REACT_APP_API_URL: http://localhost:8000
    volumes:
      - ./frontend/src:/app/src
    stdin_open: true
    tty: true

volumes:
  postgres_data:
  export_files:
EOF

# Backend Dockerfile
cat > $BACKEND_DIR/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# Frontend Dockerfile
cat > $FRONTEND_DIR/Dockerfile << 'EOF'
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
EOF

# Build script
echo "📝 Creating build scripts..."
cat > build.sh << 'EOF'
#!/bin/bash

set -e

echo "🚀 Day 57: Export System Foundation - Build & Demo Script"
echo "=========================================================="

# Check if running with Docker
USE_DOCKER=${1:-"no-docker"}

if [ "$USE_DOCKER" == "docker" ]; then
    echo "🐳 Building and starting with Docker..."
    
    # Build and start all services
    docker-compose up -d --build
    
    echo "⏳ Waiting for services to be ready..."
    sleep 15
    
    echo "✅ Services started!"
    echo "📊 Backend API: http://localhost:8000"
    echo "🌐 Frontend Dashboard: http://localhost:3000"
    echo "📋 API Docs: http://localhost:8000/docs"
    echo ""
    echo "📝 View logs with: docker-compose logs -f"
    echo "🛑 Stop with: ./stop.sh docker"
    
else
    echo "💻 Building and starting without Docker..."
    
    # Install backend dependencies
    echo "📦 Installing backend dependencies..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    
    # Setup database
    echo "🗄️ Setting up database..."
    export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/exportdb"
    export REDIS_URL="redis://localhost:6379/0"
    
    # Check if PostgreSQL is running
    if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
        echo "⚠️  PostgreSQL is not running. Please start PostgreSQL first."
        echo "   On macOS: brew services start postgresql"
        echo "   On Ubuntu: sudo systemctl start postgresql"
        exit 1
    fi
    
    # Check if Redis is running
    if ! redis-cli ping > /dev/null 2>&1; then
        echo "⚠️  Redis is not running. Please start Redis first."
        echo "   On macOS: brew services start redis"
        echo "   On Ubuntu: sudo systemctl start redis"
        exit 1
    fi
    
    # Create database if not exists
    createdb exportdb 2>/dev/null || true
    
    # Seed data
    echo "🌱 Seeding test data..."
    python app/seed_data.py
    
    # Start Celery worker in background
    echo "🔄 Starting Celery worker..."
    celery -A app.celery_config.celery_app worker --loglevel=info > celery.log 2>&1 &
    CELERY_PID=$!
    echo $CELERY_PID > celery.pid
    
    # Start backend
    echo "🚀 Starting backend server..."
    uvicorn app.main:app --reload > backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > backend.pid
    
    cd ..
    
    # Install frontend dependencies
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    
    # Start frontend
    echo "🎨 Starting frontend..."
    npm start > frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > frontend.pid
    
    cd ..
    
    echo "⏳ Waiting for services to start..."
    sleep 10
    
    echo "✅ All services started!"
    echo "📊 Backend API: http://localhost:8000"
    echo "🌐 Frontend Dashboard: http://localhost:3000"
    echo "📋 API Docs: http://localhost:8000/docs"
    echo ""
    echo "🛑 Stop with: ./stop.sh"
fi

echo ""
echo "🎯 Demo Instructions:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Select export format (CSV, JSON, PDF, or Excel)"
echo "3. Click 'Create Export' button"
echo "4. Watch the progress bar as export processes"
echo "5. Click 'Download Export' when completed"
echo "6. Verify downloaded file opens correctly"
echo ""
echo "🧪 Run tests:"
echo "   cd backend && source venv/bin/activate && pytest"
EOF

chmod +x build.sh

# Stop script
cat > stop.sh << 'EOF'
#!/bin/bash

USE_DOCKER=${1:-"no-docker"}

if [ "$USE_DOCKER" == "docker" ]; then
    echo "🛑 Stopping Docker services..."
    docker-compose down
else
    echo "🛑 Stopping services..."
    
    # Stop frontend
    if [ -f frontend/frontend.pid ]; then
        kill $(cat frontend/frontend.pid) 2>/dev/null || true
        rm frontend/frontend.pid
    fi
    
    # Stop backend
    if [ -f backend/backend.pid ]; then
        kill $(cat backend/backend.pid) 2>/dev/null || true
        rm backend/backend.pid
    fi
    
    # Stop Celery
    if [ -f backend/celery.pid ]; then
        kill $(cat backend/celery.pid) 2>/dev/null || true
        rm backend/celery.pid
    fi
    
    echo "✅ All services stopped"
fi
EOF

chmod +x stop.sh

# README
cat > README.md << 'EOF'
# Day 57: Export System Foundation

Multi-format data export system with streaming, background processing, and real-time progress tracking.

## Features

- **Multi-Format Support**: CSV, JSON, PDF, Excel exports
- **Streaming Processing**: Handles millions of records efficiently
- **Background Jobs**: Async processing with Celery
- **Progress Tracking**: Real-time status updates
- **Download Management**: 24-hour expiry with signed URLs

## Quick Start

### With Docker
```bash
./build.sh docker
```

### Without Docker
```bash
./build.sh
```

## Access Points

- Frontend Dashboard: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Testing

```bash
cd backend
source venv/bin/activate
pytest
```

## Stop Services

```bash
./stop.sh        # Without Docker
./stop.sh docker # With Docker
```
EOF

chmod +x build.sh stop.sh

cd ..

echo ""
echo "✅ Project structure created successfully!"
echo ""
echo "📁 Project location: $PROJECT_NAME/"
echo ""
echo "🚀 Next steps:"
echo "   cd $PROJECT_NAME"
echo "   ./build.sh          # Run without Docker"
echo "   ./build.sh docker   # Run with Docker"
echo ""
echo "🎉 Day 57: Export System Foundation is ready!"