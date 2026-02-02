from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.models.incident import Incident
from app.services.incident_responder import IncidentResponder
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class IncidentUpdate(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None

@router.get("/")
def get_incidents(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Retrieve incidents with filtering"""
    query = db.query(Incident)
    
    if status:
        query = query.filter(Incident.status == status)
    if severity:
        query = query.filter(Incident.severity == severity)
    
    total = query.count()
    incidents = query.order_by(Incident.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "incidents": [inc.to_dict() for inc in incidents]
    }

@router.get("/{incident_id}")
def get_incident(incident_id: str, db: Session = Depends(get_db)):
    """Retrieve specific incident"""
    incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    return incident.to_dict()

@router.patch("/{incident_id}")
def update_incident(
    incident_id: str,
    update: IncidentUpdate,
    db: Session = Depends(get_db)
):
    """Update incident status and details"""
    incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    if update.status:
        IncidentResponder.update_incident_status(
            db, incident_id, update.status, update.resolution_notes
        )
    
    if update.assigned_to:
        incident.assigned_to = update.assigned_to
        db.commit()
    
    db.refresh(incident)
    return incident.to_dict()

@router.get("/{incident_id}/timeline")
def get_incident_timeline(incident_id: str, db: Session = Depends(get_db)):
    """Get incident timeline with related events"""
    from app.models.security_event import SecurityEvent
    
    incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Get related security events
    event_ids = incident.related_events or []
    events = db.query(SecurityEvent).filter(SecurityEvent.id.in_(event_ids)).order_by(
        SecurityEvent.timestamp
    ).all() if event_ids else []
    
    return {
        "incident": incident.to_dict(),
        "timeline": [e.to_dict() for e in events],
        "response_actions": incident.response_actions
    }
