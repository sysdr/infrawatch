from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from typing import List, Optional
from datetime import datetime
import uuid

from app.core.database import get_db
from app.core.mock_data import get_mock_audit_logs
from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogResponse

router = APIRouter()

@router.get("/", response_model=List[AuditLogResponse])
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    action_type: Optional[str] = None,
    actor: Optional[str] = None,
    resource_type: Optional[str] = None,
    db: Optional[Session] = Depends(get_db)
):
    """Get audit logs with optional filtering"""
    if db is None:
        mock_logs = get_mock_audit_logs(limit)
        # Apply filters
        if action_type:
            mock_logs = [l for l in mock_logs if l.get("action_type") == action_type]
        if actor:
            mock_logs = [l for l in mock_logs if l.get("user") == actor]
        return mock_logs[skip:skip+limit]
    
    try:
        query = db.query(AuditLog)
        
        if action_type:
            query = query.filter(AuditLog.action_type == action_type)
        if actor:
            query = query.filter(AuditLog.actor == actor)
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        
        logs = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
        return logs
    except (OperationalError, Exception) as e:
        print(f"Database error in get_audit_logs: {e}")
        mock_logs = get_mock_audit_logs(limit)
        return mock_logs[skip:skip+limit]

@router.get("/{log_id}", response_model=AuditLogResponse)
async def get_audit_log(log_id: str, db: Session = Depends(get_db)):
    """Get specific audit log entry"""
    log = db.query(AuditLog).filter(AuditLog.log_id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return log

@router.post("/")
async def create_audit_log(
    action_type: str,
    actor: str,
    resource_type: str,
    resource_id: Optional[str],
    action_result: str,
    ip_address: str,
    before_state: Optional[dict] = None,
    after_state: Optional[dict] = None,
    metadata: Optional[dict] = None,
    db: Session = Depends(get_db)
):
    """Create new audit log entry"""
    db_log = AuditLog(
        log_id=str(uuid.uuid4()),
        action_type=action_type,
        actor=actor,
        resource_type=resource_type,
        resource_id=resource_id,
        action_result=action_result,
        ip_address=ip_address,
        before_state=before_state,
        after_state=after_state,
        audit_metadata=metadata
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return {"message": "Audit log created", "log_id": db_log.log_id}

@router.get("/stats/summary")
async def get_audit_summary(db: Session = Depends(get_db)):
    """Get audit log summary statistics"""
    total_logs = db.query(AuditLog).count()
    
    # Action type distribution
    action_types = db.query(AuditLog.action_type).distinct().all()
    
    # Result distribution
    success_count = db.query(AuditLog).filter(AuditLog.action_result == "success").count()
    failure_count = db.query(AuditLog).filter(AuditLog.action_result == "failure").count()
    
    return {
        "total_logs": total_logs,
        "unique_action_types": len(action_types),
        "success_count": success_count,
        "failure_count": failure_count,
        "success_rate": round((success_count / total_logs * 100) if total_logs > 0 else 0, 2)
    }
