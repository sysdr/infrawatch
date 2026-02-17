from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db, ReportSchedule, ReportDefinition
from app.api.schemas.report_schemas import ScheduleCreate
from app.services.schedulers.cron_scheduler import CronScheduler
from typing import List

router = APIRouter()

@router.post("/")
def create_schedule(schedule: ScheduleCreate, db: Session = Depends(get_db)):
    """Create a new report schedule"""
    
    # Verify report exists
    report = db.query(ReportDefinition).filter(ReportDefinition.id == schedule.report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Parse cron expression
    scheduler = CronScheduler()
    try:
        next_run = scheduler.parse_cron(schedule.cron_expression, schedule.timezone)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    db_schedule = ReportSchedule(
        report_id=schedule.report_id,
        cron_expression=schedule.cron_expression,
        timezone=schedule.timezone,
        next_run=next_run,
        is_active=True
    )
    
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    
    return db_schedule

@router.get("/")
def list_schedules(db: Session = Depends(get_db)):
    """List all schedules"""
    schedules = db.query(ReportSchedule).filter(ReportSchedule.is_active == True).all()
    return schedules

@router.delete("/{schedule_id}")
def delete_schedule(schedule_id: int, db: Session = Depends(get_db)):
    """Deactivate a schedule"""
    schedule = db.query(ReportSchedule).filter(ReportSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    schedule.is_active = False
    db.commit()
    
    return {"status": "deactivated"}
