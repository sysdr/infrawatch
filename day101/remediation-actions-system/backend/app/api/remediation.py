from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from ..core.database import get_db
from ..models.remediation import (
    RemediationAction, ActionTemplate, ApprovalRequest,
    ActionStatus, RiskLevel
)
from ..services.remediation import RemediationService

router = APIRouter()

class TemplateCreate(BaseModel):
    name: str
    description: str
    risk_level: RiskLevel
    script_name: str
    parameters_schema: dict
    requires_approval: bool = False
    max_blast_radius: int = 100
    can_rollback: bool = True
    rollback_script: Optional[str] = None

class ActionCreate(BaseModel):
    template_id: int
    incident_id: str
    parameters: dict
    created_by: str = "system"

class ActionResponse(BaseModel):
    id: int
    template_id: int
    template_name: str
    incident_id: str
    status: ActionStatus
    risk_score: float
    blast_radius: int
    created_at: datetime
    approved_at: Optional[datetime]
    executed_at: Optional[datetime]
    completed_at: Optional[datetime]
    parameters: Optional[dict] = None
    can_rollback: bool = False
    
    class Config:
        from_attributes = True

class ApprovalResponse(BaseModel):
    action_id: int
    approver: str
    comments: Optional[str]

@router.post("/templates", response_model=dict)
async def create_template(template: TemplateCreate, db: Session = Depends(get_db)):
    db_template = ActionTemplate(**template.model_dump())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return {"id": db_template.id, "name": db_template.name}

@router.get("/templates", response_model=List[dict])
async def list_templates(db: Session = Depends(get_db)):
    templates = db.query(ActionTemplate).all()
    return [
        {"id": t.id, "name": t.name, "description": t.description,
         "risk_level": t.risk_level.value, "requires_approval": t.requires_approval}
        for t in templates
    ]

@router.post("/actions", response_model=dict)
async def create_action(action: ActionCreate, db: Session = Depends(get_db)):
    service = RemediationService(db)
    db_action = await service.create_action(
        action.template_id, action.incident_id, action.parameters, action.created_by
    )
    return {
        "id": db_action.id, "template_id": db_action.template_id,
        "template_name": db_action.template.name, "incident_id": db_action.incident_id,
        "status": db_action.status, "risk_score": db_action.risk_score,
        "blast_radius": db_action.blast_radius, "created_at": db_action.created_at,
        "approved_at": db_action.approved_at, "executed_at": db_action.executed_at,
        "completed_at": db_action.completed_at,
        "can_rollback": db_action.template.can_rollback and db_action.status == ActionStatus.COMPLETED
    }

@router.get("/actions", response_model=List[dict])
async def list_actions(
    status: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(RemediationAction)
    if status:
        query = query.filter(RemediationAction.status == status)
    actions = query.order_by(RemediationAction.created_at.desc()).limit(limit).all()
    return [
        {
            "id": a.id, "template_id": a.template_id, "template_name": a.template.name,
            "incident_id": a.incident_id, "status": a.status, "risk_score": a.risk_score,
            "blast_radius": a.blast_radius, "created_at": a.created_at,
            "approved_at": a.approved_at, "executed_at": a.executed_at,
            "completed_at": a.completed_at, "parameters": a.parameters,
            "can_rollback": a.template.can_rollback and a.status == ActionStatus.COMPLETED
        }
        for a in actions
    ]

@router.get("/actions/{action_id}", response_model=dict)
async def get_action(action_id: int, db: Session = Depends(get_db)):
    action = db.query(RemediationAction).filter(RemediationAction.id == action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    return {
        "id": action.id, "template_name": action.template.name,
        "incident_id": action.incident_id, "status": action.status.value,
        "risk_score": action.risk_score, "blast_radius": action.blast_radius,
        "parameters": action.parameters, "dry_run_result": action.dry_run_result,
        "execution_result": action.execution_result,
        "created_at": action.created_at.isoformat(),
        "approved_at": action.approved_at.isoformat() if action.approved_at else None,
        "executed_at": action.executed_at.isoformat() if action.executed_at else None,
        "can_rollback": action.template.can_rollback and action.status == ActionStatus.COMPLETED
    }

@router.post("/actions/{action_id}/approve", response_model=dict)
async def approve_action(
    action_id: int,
    approval: ApprovalResponse,
    db: Session = Depends(get_db)
):
    service = RemediationService(db)
    action = await service.approve_action(action_id, approval.approver, approval.comments or "")
    return {
        "id": action.id, "template_id": action.template_id, "template_name": action.template.name,
        "incident_id": action.incident_id, "status": action.status,
        "risk_score": action.risk_score, "blast_radius": action.blast_radius,
        "created_at": action.created_at, "approved_at": action.approved_at,
        "executed_at": action.executed_at, "completed_at": action.completed_at
    }

@router.post("/actions/{action_id}/reject")
async def reject_action(action_id: int, db: Session = Depends(get_db)):
    action = db.query(RemediationAction).filter(RemediationAction.id == action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    action.status = ActionStatus.REJECTED
    db.commit()
    return {"status": "rejected"}

@router.post("/actions/{action_id}/rollback", response_model=dict)
async def rollback_action(action_id: int, db: Session = Depends(get_db)):
    service = RemediationService(db)
    try:
        result = await service.rollback_action(action_id)
        return {"status": "rolled_back", "result": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/stats", response_model=dict)
async def get_stats(db: Session = Depends(get_db)):
    total = db.query(RemediationAction).count()
    pending = db.query(RemediationAction).filter(RemediationAction.status == ActionStatus.PENDING).count()
    completed = db.query(RemediationAction).filter(RemediationAction.status == ActionStatus.COMPLETED).count()
    failed = db.query(RemediationAction).filter(RemediationAction.status == ActionStatus.FAILED).count()
    return {
        "total_actions": total,
        "pending": pending,
        "completed": completed,
        "failed": failed,
        "success_rate": round((completed / total * 100) if total > 0 else 0, 2)
    }
