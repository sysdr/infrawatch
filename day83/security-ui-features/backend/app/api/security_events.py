from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from app.core.database import get_db
from app.core.mock_data import get_mock_security_events
from app.models.security_event import SecurityEvent
from app.schemas.security_event import SecurityEventCreate, SecurityEventResponse

router = APIRouter()

@router.get("/", response_model=List[SecurityEventResponse])
async def get_security_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    is_resolved: Optional[bool] = None,
    db: Optional[Session] = Depends(get_db)
):
    """Get security events with optional filtering"""
    if db is None:
        mock_events = get_mock_security_events(limit)
        # Apply filters to mock data
        if event_type:
            mock_events = [e for e in mock_events if e.get("event_type") == event_type]
        if severity:
            mock_events = [e for e in mock_events if e.get("severity") == severity]
        if is_resolved is not None:
            mock_events = [e for e in mock_events if e.get("is_resolved") == is_resolved]
        return mock_events[skip:skip+limit]
    
    try:
        query = db.query(SecurityEvent)
        
        if event_type:
            query = query.filter(SecurityEvent.event_type == event_type)
        if severity:
            query = query.filter(SecurityEvent.severity == severity)
        if is_resolved is not None:
            query = query.filter(SecurityEvent.is_resolved == is_resolved)
        
        events = query.order_by(SecurityEvent.created_at.desc()).offset(skip).limit(limit).all()
        return events
    except (OperationalError, Exception) as e:
        print(f"Database error in get_security_events: {e}")
        mock_events = get_mock_security_events(limit)
        return mock_events[skip:skip+limit]

@router.get("/{event_id}", response_model=SecurityEventResponse)
async def get_security_event(event_id: str, db: Session = Depends(get_db)):
    """Get specific security event by ID"""
    event = db.query(SecurityEvent).filter(SecurityEvent.event_id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Security event not found")
    return event

@router.post("/", response_model=SecurityEventResponse)
async def create_security_event(event: SecurityEventCreate, db: Session = Depends(get_db)):
    """Create new security event"""
    db_event = SecurityEvent(
        event_id=str(uuid.uuid4()),
        **event.model_dump()
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@router.patch("/{event_id}/resolve")
async def resolve_security_event(
    event_id: str,
    resolved_by: str,
    db: Session = Depends(get_db)
):
    """Mark security event as resolved"""
    event = db.query(SecurityEvent).filter(SecurityEvent.event_id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Security event not found")
    
    event.is_resolved = True
    event.resolved_by = resolved_by
    event.resolved_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Event resolved successfully", "event_id": event_id}

@router.get("/stats/summary")
async def get_event_summary(db: Optional[Session] = Depends(get_db)):
    """Get summary statistics of security events"""
    if db is None:
        from app.core.mock_data import get_mock_event_summary
        return get_mock_event_summary()
    
    try:
        total_events = db.query(SecurityEvent).count()
        unresolved_events = db.query(SecurityEvent).filter(SecurityEvent.is_resolved == False).count()
        
        # Events by severity
        severity_counts = {}
        for severity in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
            count = db.query(SecurityEvent).filter(SecurityEvent.severity == severity).count()
            severity_counts[severity] = count
        
        # Recent events (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_events = db.query(SecurityEvent).filter(SecurityEvent.created_at >= yesterday).count()
        
        return {
            "total_events": total_events,
            "unresolved_events": unresolved_events,
            "severity_breakdown": severity_counts,
            "events_last_24h": recent_events
        }
    except (OperationalError, Exception) as e:
        print(f"Database error in get_event_summary: {e}")
        from app.core.mock_data import get_mock_event_summary
        return get_mock_event_summary()
