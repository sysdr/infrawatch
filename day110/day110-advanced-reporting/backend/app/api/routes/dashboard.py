from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.database import get_db, ReportTemplate, ReportDefinition, ReportSchedule, DistributionList, ReportExecution, ReportState

router = APIRouter()

@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Return counts for dashboard metrics (templates, reports, schedules, distribution lists, executions)."""
    templates_count = db.query(ReportTemplate).filter(ReportTemplate.is_active == True).count()
    reports_count = db.query(ReportDefinition).count()
    schedules_count = db.query(ReportSchedule).filter(ReportSchedule.is_active == True).count()
    distribution_lists_count = db.query(DistributionList).count()
    executions_total = db.query(ReportExecution).count()
    executions_completed = db.query(ReportExecution).filter(ReportExecution.state == ReportState.COMPLETED).count()
    executions_failed = db.query(ReportExecution).filter(ReportExecution.state == ReportState.FAILED).count()
    return {
        "templates": templates_count,
        "reports": reports_count,
        "schedules": schedules_count,
        "distribution_lists": distribution_lists_count,
        "executions_total": executions_total,
        "executions_completed": executions_completed,
        "executions_failed": executions_failed,
    }
