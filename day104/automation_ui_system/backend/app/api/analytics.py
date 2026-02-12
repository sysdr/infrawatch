from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.workflow import WorkflowExecution, ExecutionStatus, Workflow

router = APIRouter()

@router.get("/analytics/overview")
def get_analytics_overview(db: Session = Depends(get_db)):
    total_workflows = db.query(Workflow).count()
    total_executions = db.query(WorkflowExecution).count()
    
    success_count = db.query(WorkflowExecution).filter(WorkflowExecution.status == ExecutionStatus.SUCCESS).count()
    failed_count = db.query(WorkflowExecution).filter(WorkflowExecution.status == ExecutionStatus.FAILED).count()
    running_count = db.query(WorkflowExecution).filter(WorkflowExecution.status == ExecutionStatus.RUNNING).count()
    
    success_rate = (success_count / total_executions * 100) if total_executions > 0 else 0
    
    avg_duration = db.query(func.avg(WorkflowExecution.duration_seconds)).filter(
        WorkflowExecution.duration_seconds.isnot(None)
    ).scalar() or 0
    
    return {
        "total_workflows": total_workflows,
        "total_executions": total_executions,
        "success_count": success_count,
        "failed_count": failed_count,
        "running_count": running_count,
        "success_rate": round(success_rate, 2),
        "avg_duration_seconds": round(float(avg_duration), 2)
    }

@router.get("/analytics/executions/timeline")
def get_execution_timeline(days: int = 7, db: Session = Depends(get_db)):
    start_date = datetime.utcnow() - timedelta(days=days)
    
    executions = db.query(
        func.date(WorkflowExecution.created_at).label("date"),
        WorkflowExecution.status,
        func.count(WorkflowExecution.id).label("count")
    ).filter(
        WorkflowExecution.created_at >= start_date
    ).group_by(
        func.date(WorkflowExecution.created_at),
        WorkflowExecution.status
    ).all()
    
    timeline = {}
    for date, status, count in executions:
        date_str = date.isoformat()
        if date_str not in timeline:
            timeline[date_str] = {}
        timeline[date_str][status.value] = count
    
    return {"timeline": timeline}

@router.get("/analytics/workflows/top")
def get_top_workflows(limit: int = 10, db: Session = Depends(get_db)):
    top_workflows = db.query(
        Workflow.id,
        Workflow.name,
        func.count(WorkflowExecution.id).label("execution_count"),
        func.avg(WorkflowExecution.duration_seconds).label("avg_duration")
    ).join(
        WorkflowExecution
    ).group_by(
        Workflow.id,
        Workflow.name
    ).order_by(
        func.count(WorkflowExecution.id).desc()
    ).limit(limit).all()
    
    return {
        "top_workflows": [
            {
                "id": wf.id,
                "name": wf.name,
                "execution_count": wf.execution_count,
                "avg_duration": round(float(wf.avg_duration), 2) if wf.avg_duration else 0
            }
            for wf in top_workflows
        ]
    }
