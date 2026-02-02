from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.models.security_event import SecurityEvent
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter()

@router.get("/trail")
def get_audit_trail(
    user_id: Optional[str] = None,
    resource: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Retrieve audit trail with filtering"""
    query = db.query(SecurityEvent)
    
    if user_id:
        query = query.filter(SecurityEvent.user_id == user_id)
    if resource:
        query = query.filter(SecurityEvent.resource.ilike(f"%{resource}%"))
    
    if start_date:
        start = datetime.fromisoformat(start_date)
        query = query.filter(SecurityEvent.timestamp >= start)
    else:
        # Default to last 7 days
        week_ago = datetime.utcnow() - timedelta(days=7)
        query = query.filter(SecurityEvent.timestamp >= week_ago)
    
    if end_date:
        end = datetime.fromisoformat(end_date)
        query = query.filter(SecurityEvent.timestamp <= end)
    
    total = query.count()
    events = query.order_by(SecurityEvent.timestamp.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "audit_trail": [event.to_dict() for event in events]
    }

@router.get("/verify")
def verify_audit_integrity(
    start_id: int = Query(1),
    count: int = Query(100, le=1000),
    db: Session = Depends(get_db)
):
    """Verify audit trail integrity using hash chain"""
    events = db.query(SecurityEvent).filter(
        SecurityEvent.id >= start_id
    ).order_by(SecurityEvent.id).limit(count).all()
    
    if not events:
        return {"status": "no_events", "verified": True}
    
    violations = []
    for i in range(1, len(events)):
        expected_prev = events[i-1].event_hash
        actual_prev = events[i].previous_hash
        
        if expected_prev != actual_prev:
            violations.append({
                "event_id": events[i].id,
                "expected_previous_hash": expected_prev,
                "actual_previous_hash": actual_prev
            })
    
    return {
        "events_checked": len(events),
        "verified": len(violations) == 0,
        "violations": violations
    }

@router.get("/user/{user_id}")
def get_user_audit_history(
    user_id: str,
    days: int = Query(30, le=365),
    db: Session = Depends(get_db)
):
    """Get complete audit history for a user"""
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    events = db.query(SecurityEvent).filter(
        SecurityEvent.user_id == user_id,
        SecurityEvent.timestamp >= cutoff
    ).order_by(SecurityEvent.timestamp.desc()).all()
    
    # Aggregate statistics
    from collections import Counter
    event_types = Counter(e.event_type for e in events)
    resources_accessed = Counter(e.resource for e in events if e.resource)
    
    return {
        "user_id": user_id,
        "period_days": days,
        "total_events": len(events),
        "events_by_type": dict(event_types),
        "resources_accessed": dict(resources_accessed.most_common(10)),
        "recent_events": [e.to_dict() for e in events[:20]]
    }
