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
