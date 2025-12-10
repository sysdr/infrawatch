from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ExportJob, ScheduledExport
from app.schemas import ExportRequest, ExportResponse, ExportStatus, ScheduleRequest, ScheduleResponse
from app.services.export_service import ExportService
from app.websocket.manager import manager
from datetime import datetime, timedelta
from typing import List
import uuid
import asyncio
import os
from croniter import croniter
import pytz

router = APIRouter()
export_service = ExportService()

async def process_export(job_id: str, db: Session):
    """Background task to process export"""
    job = db.query(ExportJob).filter(ExportJob.job_id == job_id).first()
    if not job:
        return
    
    try:
        # Update status to processing
        job.status = "PROCESSING"
        job.started_at = datetime.now()
        db.commit()
        
        await manager.send_progress(job_id, {
            "job_id": job_id,
            "status": "PROCESSING",
            "progress": 10,
            "stage": "Fetching data"
        })
        
        # Simulate data fetching
        await asyncio.sleep(1)
        config = job.config
        data = export_service.generate_sample_data(config.get("row_count", 100))
        
        await manager.send_progress(job_id, {
            "job_id": job_id,
            "progress": 50,
            "stage": "Converting format"
        })
        
        # Convert to requested format
        await asyncio.sleep(1)
        format_type = job.format_type
        options = config.get("options", {})
        
        if format_type == "CSV":
            content = export_service.export_to_csv(data, options)
            filename = f"{job_id}.csv"
            with open(f"/tmp/exports/{filename}", "w") as f:
                f.write(content)
            filepath = f"/tmp/exports/{filename}"
        elif format_type == "JSON":
            content = export_service.export_to_json(data, options)
            filename = f"{job_id}.json"
            with open(f"/tmp/exports/{filename}", "w") as f:
                f.write(content)
            filepath = f"/tmp/exports/{filename}"
        elif format_type == "EXCEL":
            filepath = export_service.export_to_excel(data, options)
        elif format_type == "PDF":
            filepath = export_service.export_to_pdf(data, options)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
        
        await manager.send_progress(job_id, {
            "job_id": job_id,
            "progress": 90,
            "stage": "Generating download link"
        })
        
        # Update job with results
        await asyncio.sleep(0.5)
        job.status = "COMPLETED"
        job.file_path = filepath
        job.file_size = len(open(filepath, "rb").read()) if filepath else 0
        job.row_count = len(data)
        job.progress = 100.0
        job.completed_at = datetime.now()
        job.expires_at = datetime.now() + timedelta(hours=24)
        job.download_url = f"/api/exports/{job_id}/download"
        db.commit()
        
        await manager.send_progress(job_id, {
            "job_id": job_id,
            "status": "COMPLETED",
            "progress": 100,
            "stage": "Complete",
            "download_url": job.download_url,
            "file_size": job.file_size,
            "row_count": job.row_count
        })
        
    except Exception as e:
        job.status = "FAILED"
        job.error_message = str(e)
        job.completed_at = datetime.now()
        db.commit()
        
        await manager.send_progress(job_id, {
            "job_id": job_id,
            "status": "FAILED",
            "error": str(e)
        })

@router.post("/exports", response_model=ExportResponse)
async def create_export(
    request: ExportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new export job"""
    job_id = str(uuid.uuid4())
    
    job = ExportJob(
        job_id=job_id,
        user_id=request.user_id,
        status="QUEUED",
        format_type=request.config.format_type,
        config=request.config.dict()
    )
    
    db.add(job)
    db.commit()
    
    # Start background processing
    background_tasks.add_task(process_export, job_id, db)
    
    return ExportResponse(
        job_id=job_id,
        status="QUEUED",
        message="Export job created successfully"
    )

@router.get("/exports/{job_id}", response_model=ExportStatus)
def get_export_status(job_id: str, db: Session = Depends(get_db)):
    """Get status of an export job"""
    job = db.query(ExportJob).filter(ExportJob.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Export job not found")
    
    return ExportStatus(
        job_id=job.job_id,
        status=job.status,
        progress=job.progress or 0.0,
        format_type=job.format_type,
        file_size=job.file_size,
        row_count=job.row_count,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        download_url=job.download_url,
        error_message=job.error_message
    )

@router.get("/exports/{job_id}/download")
def download_export(job_id: str, db: Session = Depends(get_db)):
    """Download completed export"""
    from fastapi.responses import FileResponse
    
    job = db.query(ExportJob).filter(ExportJob.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Export job not found")
    
    if job.status != "COMPLETED":
        raise HTTPException(status_code=400, detail="Export not completed")
    
    if not job.file_path or not os.path.exists(job.file_path):
        raise HTTPException(status_code=404, detail="Export file not found")
    
    if job.expires_at and datetime.now() > job.expires_at:
        raise HTTPException(status_code=410, detail="Export has expired")
    
    filename = os.path.basename(job.file_path)
    return FileResponse(
        job.file_path,
        media_type="application/octet-stream",
        filename=filename
    )

@router.delete("/exports/{job_id}")
def cancel_export(job_id: str, db: Session = Depends(get_db)):
    """Cancel an export job"""
    job = db.query(ExportJob).filter(ExportJob.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Export job not found")
    
    if job.status in ["COMPLETED", "FAILED", "CANCELLED"]:
        raise HTTPException(status_code=400, detail="Cannot cancel job in current state")
    
    job.status = "CANCELLED"
    job.completed_at = datetime.now()
    db.commit()
    
    return {"message": "Export cancelled successfully"}

@router.get("/exports", response_model=List[ExportStatus])
def list_exports(
    user_id: str,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """List export jobs for a user"""
    jobs = db.query(ExportJob)\
        .filter(ExportJob.user_id == user_id)\
        .order_by(ExportJob.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return [
        ExportStatus(
            job_id=job.job_id,
            status=job.status,
            progress=job.progress or 0.0,
            format_type=job.format_type,
            file_size=job.file_size,
            row_count=job.row_count,
            created_at=job.created_at,
            started_at=job.started_at,
            completed_at=job.completed_at,
            download_url=job.download_url,
            error_message=job.error_message
        )
        for job in jobs
    ]

@router.post("/schedules", response_model=ScheduleResponse)
def create_schedule(request: ScheduleRequest, db: Session = Depends(get_db)):
    """Create a scheduled export"""
    schedule_id = str(uuid.uuid4())
    
    # Calculate next run time
    tz = pytz.timezone(request.timezone)
    base_time = datetime.now(tz)
    cron = croniter(request.cron_expression, base_time)
    next_run = cron.get_next(datetime)
    
    schedule = ScheduledExport(
        schedule_id=schedule_id,
        user_id=request.user_id,
        name=request.name,
        cron_expression=request.cron_expression,
        timezone=request.timezone,
        export_config=request.export_config.dict(),
        next_run_time=next_run
    )
    
    db.add(schedule)
    db.commit()
    
    return ScheduleResponse(
        schedule_id=schedule_id,
        name=request.name,
        cron_expression=request.cron_expression,
        next_run_time=next_run,
        message="Schedule created successfully"
    )

@router.get("/schedules")
def list_schedules(user_id: str, db: Session = Depends(get_db)):
    """List scheduled exports for a user"""
    schedules = db.query(ScheduledExport)\
        .filter(ScheduledExport.user_id == user_id)\
        .order_by(ScheduledExport.created_at.desc())\
        .all()
    
    return schedules

@router.delete("/schedules/{schedule_id}")
def delete_schedule(schedule_id: str, db: Session = Depends(get_db)):
    """Delete a scheduled export"""
    schedule = db.query(ScheduledExport).filter(
        ScheduledExport.schedule_id == schedule_id
    ).first()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    db.delete(schedule)
    db.commit()
    
    return {"message": "Schedule deleted successfully"}

@router.get("/preview")
def get_preview(
    format_type: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get preview data for export"""
    data = export_service.generate_sample_data(limit)
    
    options = {}
    if format_type == "CSV":
        preview = export_service.export_to_csv(data, options)
        return {"format": "CSV", "preview": preview, "data": data}
    elif format_type == "JSON":
        preview = export_service.export_to_json(data, options)
        return {"format": "JSON", "preview": preview, "data": data}
    else:
        return {"format": format_type, "data": data}
