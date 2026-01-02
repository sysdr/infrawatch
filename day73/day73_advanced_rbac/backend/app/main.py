from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, List, Optional
import redis
import os

from .models import get_db, engine, Base
from .models.permission_models import User, Role, Team, PermissionPolicy, Resource, AuditEvent, ComplianceViolation
from .services.permission_engine import PermissionEngine
from .services.audit_service import AuditService
from .services.compliance_monitor import ComplianceMonitor

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Advanced RBAC System")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

# Pydantic models
class PermissionCheckRequest(BaseModel):
    subject_id: str
    action: str
    resource_type: str
    resource_id: str
    context: Optional[Dict] = None

class PermissionCheckResponse(BaseModel):
    allowed: bool
    reason: str
    policy_matched: str

class PolicyCreate(BaseModel):
    name: str
    subject_type: str
    subject_id: str
    action: str
    resource_type: str
    resource_id: Optional[str] = "*"
    effect: str
    conditions: Optional[Dict] = None
    priority: int = 0

class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    parent_role_id: Optional[int] = None

class TeamCreate(BaseModel):
    name: str
    description: Optional[str] = None
    parent_team_id: Optional[int] = None

# Permission Evaluation Endpoint
@app.post("/api/permissions/evaluate", response_model=PermissionCheckResponse)
def evaluate_permission(
    request: PermissionCheckRequest,
    db: Session = Depends(get_db)
):
    """Evaluate permission request."""
    engine = PermissionEngine(db, redis_client)
    audit = AuditService(db)
    
    allowed, reason, policy = engine.evaluate(
        request.subject_id,
        request.action,
        request.resource_type,
        request.resource_id,
        request.context
    )
    
    # Log audit event
    subject_type, subject_id = request.subject_id.split(':', 1)
    audit.log_event(
        subject_type=subject_type,
        subject_id=subject_id,
        action=request.action,
        resource_type=request.resource_type,
        resource_id=request.resource_id,
        decision='allowed' if allowed else 'denied',
        reason=reason,
        policy_matched=policy,
        context=request.context
    )
    
    return PermissionCheckResponse(
        allowed=allowed,
        reason=reason,
        policy_matched=policy
    )

# Policy Management
@app.post("/api/policies")
def create_policy(policy: PolicyCreate, db: Session = Depends(get_db)):
    """Create new permission policy."""
    db_policy = PermissionPolicy(**policy.dict())
    db.add(db_policy)
    db.commit()
    db.refresh(db_policy)
    
    # Invalidate cache
    engine = PermissionEngine(db, redis_client)
    engine.invalidate_cache()
    
    return db_policy

@app.get("/api/policies")
def list_policies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all policies."""
    policies = db.query(PermissionPolicy).offset(skip).limit(limit).all()
    return policies

@app.delete("/api/policies/{policy_id}")
def delete_policy(policy_id: int, db: Session = Depends(get_db)):
    """Delete policy."""
    policy = db.query(PermissionPolicy).filter(PermissionPolicy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    db.delete(policy)
    db.commit()
    
    # Invalidate cache
    engine = PermissionEngine(db, redis_client)
    engine.invalidate_cache()
    
    return {"status": "deleted"}

# Role Management
@app.post("/api/roles")
def create_role(role: RoleCreate, db: Session = Depends(get_db)):
    """Create new role."""
    db_role = Role(**role.dict())
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

@app.get("/api/roles")
def list_roles(db: Session = Depends(get_db)):
    """List all roles."""
    roles = db.query(Role).all()
    return roles

# Team Management
@app.post("/api/teams")
def create_team(team: TeamCreate, db: Session = Depends(get_db)):
    """Create new team."""
    db_team = Team(**team.dict())
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team

@app.get("/api/teams")
def list_teams(db: Session = Depends(get_db)):
    """List all teams."""
    teams = db.query(Team).all()
    return teams

# Audit Logs
@app.get("/api/audit/events")
def get_audit_events(
    limit: int = 100,
    subject_id: Optional[str] = None,
    resource_type: Optional[str] = None,
    decision: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get audit events."""
    audit = AuditService(db)
    filters = {}
    if subject_id:
        filters['subject_id'] = subject_id
    if resource_type:
        filters['resource_type'] = resource_type
    if decision:
        filters['decision'] = decision
    
    events = audit.get_recent_events(limit=limit, filters=filters)
    return events

@app.get("/api/audit/stats")
def get_audit_stats(time_range_hours: int = 24, db: Session = Depends(get_db)):
    """Get audit statistics."""
    audit = AuditService(db)
    return audit.get_event_stats(time_range_hours)

# Compliance
@app.get("/api/compliance/violations")
def get_violations(db: Session = Depends(get_db)):
    """Get active compliance violations."""
    monitor = ComplianceMonitor(db)
    violations = monitor.get_active_violations()
    return violations

@app.post("/api/compliance/check")
def check_compliance(db: Session = Depends(get_db)):
    """Run compliance checks."""
    monitor = ComplianceMonitor(db)
    violations = monitor.check_violations()
    db.commit()
    return {"violations_found": len(violations), "violations": violations}

@app.post("/api/compliance/violations/{violation_id}/resolve")
def resolve_violation(violation_id: int, notes: str, db: Session = Depends(get_db)):
    """Resolve compliance violation."""
    monitor = ComplianceMonitor(db)
    violation = monitor.resolve_violation(violation_id, notes)
    if not violation:
        raise HTTPException(status_code=404, detail="Violation not found")
    return violation

# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "advanced-rbac"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
