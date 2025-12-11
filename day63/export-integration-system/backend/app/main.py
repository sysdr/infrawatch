from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime, timedelta

from app.database import get_db, engine
from app.models import export_job, export_schedule, export_history
from app.schemas.export_schemas import (
    ExportJobCreate, ExportJobResponse,
    ExportScheduleCreate, ExportScheduleResponse
)
from app.models.export_job import ExportJob, JobStatus
from app.models.export_schedule import ExportSchedule
from app.models.export_history import ExportHistory
from workers.export_tasks import process_export_job
from app.services.scheduler_service import export_scheduler

# Create tables
export_job.Base.metadata.create_all(bind=engine)
export_schedule.Base.metadata.create_all(bind=engine)
export_history.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Export Integration API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize scheduler on startup"""
    export_scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    """Stop scheduler on shutdown"""
    export_scheduler.stop()

# Export Job endpoints
@app.post("/api/exports", response_model=ExportJobResponse)
async def create_export_job(
    job_data: ExportJobCreate,
    db: Session = Depends(get_db)
):
    """Create new export job"""
    
    job_id = str(uuid.uuid4())
    
    job = ExportJob(
        id=job_id,
        user_id="demo-user",  # In production, get from auth
        export_type=job_data.export_type,
        format=job_data.format,
        filters=job_data.filters,
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Queue job for processing
    process_export_job.delay(job_id)
    
    return job

@app.get("/api/exports", response_model=List[ExportJobResponse])
async def list_export_jobs(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """List export jobs"""
    jobs = db.query(ExportJob).order_by(ExportJob.created_at.desc()).offset(skip).limit(limit).all()
    return jobs

@app.get("/api/exports/{job_id}", response_model=ExportJobResponse)
async def get_export_job(job_id: str, db: Session = Depends(get_db)):
    """Get export job details"""
    job = db.query(ExportJob).filter(ExportJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.get("/api/exports/{job_id}/download")
async def download_export(job_id: str, db: Session = Depends(get_db)):
    """Download export file"""
    from fastapi.responses import FileResponse
    
    job = db.query(ExportJob).filter(ExportJob.id == job_id).first()
    if not job or job.status != JobStatus.COMPLETED:
        raise HTTPException(status_code=404, detail="Export not ready")
    
    return FileResponse(
        job.file_path,
        media_type='application/octet-stream',
        filename=f"export_{job_id}.{job.format}"
    )

# Export Schedule endpoints
@app.post("/api/schedules", response_model=ExportScheduleResponse)
async def create_export_schedule(
    schedule_data: ExportScheduleCreate,
    db: Session = Depends(get_db)
):
    """Create scheduled export"""
    
    schedule_id = str(uuid.uuid4())
    
    schedule = ExportSchedule(
        id=schedule_id,
        user_id="demo-user",
        name=schedule_data.name,
        export_type=schedule_data.export_type,
        format=schedule_data.format,
        filters=schedule_data.filters,
        schedule_expression=schedule_data.schedule_expression,
        timezone=schedule_data.timezone,
        email_recipients=schedule_data.email_recipients
    )
    
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    
    # Add to scheduler
    export_scheduler.add_schedule(schedule)
    
    return schedule

@app.get("/api/schedules", response_model=List[ExportScheduleResponse])
async def list_export_schedules(db: Session = Depends(get_db)):
    """List export schedules"""
    schedules = db.query(ExportSchedule).order_by(ExportSchedule.created_at.desc()).all()
    return schedules

@app.delete("/api/schedules/{schedule_id}")
async def delete_export_schedule(schedule_id: str, db: Session = Depends(get_db)):
    """Delete export schedule"""
    schedule = db.query(ExportSchedule).filter(ExportSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    export_scheduler.remove_schedule(schedule_id)
    db.delete(schedule)
    db.commit()
    
    return {"message": "Schedule deleted"}

@app.get("/api/schedules/{schedule_id}/history")
async def get_schedule_history(schedule_id: str, db: Session = Depends(get_db)):
    """Get execution history for schedule"""
    history = db.query(ExportHistory).filter(
        ExportHistory.schedule_id == schedule_id
    ).order_by(ExportHistory.created_at.desc()).limit(50).all()
    
    return history

# Stats endpoint
@app.get("/api/stats")
async def get_export_stats(db: Session = Depends(get_db)):
    """Get export system statistics"""
    
    total_jobs = db.query(ExportJob).count()
    completed_jobs = db.query(ExportJob).filter(ExportJob.status == JobStatus.COMPLETED).count()
    failed_jobs = db.query(ExportJob).filter(ExportJob.status == JobStatus.FAILED).count()
    pending_jobs = db.query(ExportJob).filter(ExportJob.status == JobStatus.PENDING).count()
    
    total_schedules = db.query(ExportSchedule).count()
    active_schedules = db.query(ExportSchedule).filter(ExportSchedule.enabled == True).count()
    
    return {
        "total_jobs": total_jobs,
        "completed_jobs": completed_jobs,
        "failed_jobs": failed_jobs,
        "pending_jobs": pending_jobs,
        "total_schedules": total_schedules,
        "active_schedules": active_schedules
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
