from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.export_job import ExportJob, ExportStatus, ExportFormat
from app.models.notification import Notification, NotificationType
from app.tasks.export_tasks import generate_export
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
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
    if job.expires_at and datetime.now(timezone.utc) > job.expires_at:
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
