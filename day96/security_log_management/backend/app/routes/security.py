from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.models.security_event import SecurityEvent
from app.services.threat_detector import ThreatDetector
from app.services.incident_responder import IncidentResponder
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

router = APIRouter()

class SecurityEventCreate(BaseModel):
    event_type: str
    severity: str
    user_id: Optional[str] = None
    username: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    result: str
    details: Optional[Dict] = None

@router.post("/events")
def log_security_event(
    event: SecurityEventCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Log a security event and perform threat detection"""
    
    # Get previous event hash for chain
    last_event = db.query(SecurityEvent).order_by(SecurityEvent.id.desc()).first()
    previous_hash = last_event.event_hash if last_event else "0" * 64
    
    # Create security event
    security_event = SecurityEvent(
        event_type=event.event_type,
        severity=event.severity,
        user_id=event.user_id,
        username=event.username,
        ip_address=event.ip_address or request.client.host,
        user_agent=event.user_agent,
        resource=event.resource,
        action=event.action,
        result=event.result,
        details=event.details,
        previous_hash=previous_hash,
        correlation_id=getattr(request.state, "correlation_id", ""),
        timestamp=datetime.utcnow()
    )
    
    # Calculate event hash
    security_event.event_hash = security_event.calculate_hash()
    
    # Threat detection
    threats = []
    
    # Brute force detection
    if event.result == "failure":
        threat = ThreatDetector.detect_brute_force(
            event.user_id,
            security_event.ip_address,
            event.event_type
        )
        if threat.get("threat_detected"):
            threats.append(threat)
    
    # Anomaly detection
    if event.user_id:
        anomaly_score = ThreatDetector.calculate_anomaly_score(
            db, event.user_id, event.event_type, event.action
        )
        security_event.anomaly_score = anomaly_score
        
        if anomaly_score > 3.0:
            threats.append({
                "threat_detected": True,
                "threat_type": "anomalous_behavior",
                "severity": "medium",
                "anomaly_score": anomaly_score
            })
    
    # Privilege escalation detection
    if event.event_type == "authorization" and event.result == "failure":
        threat = ThreatDetector.detect_privilege_escalation(db, event.user_id)
        if threat.get("threat_detected"):
            threats.append(threat)
    
    security_event.threat_indicators = threats if threats else None
    
    db.add(security_event)
    db.commit()
    db.refresh(security_event)
    
    # Create incident for high-severity threats
    if threats and any(t.get("severity") in ["high", "critical"] for t in threats):
        related_events = ThreatDetector.correlate_events(
            db, security_event.correlation_id
        )
        
        for threat in threats:
            if threat.get("severity") in ["high", "critical"]:
                IncidentResponder.create_incident(db, threat, related_events)
    
    return {
        "event_id": security_event.id,
        "threat_detected": len(threats) > 0,
        "threats": threats,
        "event_hash": security_event.event_hash
    }

@router.get("/events")
def get_security_events(
    skip: int = 0,
    limit: int = 50,
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    user_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Retrieve security events with filtering"""
    query = db.query(SecurityEvent)
    
    if event_type:
        query = query.filter(SecurityEvent.event_type == event_type)
    if severity:
        query = query.filter(SecurityEvent.severity == severity)
    if user_id:
        query = query.filter(SecurityEvent.user_id == user_id)
    
    total = query.count()
    events = query.order_by(SecurityEvent.timestamp.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "events": [event.to_dict() for event in events]
    }

@router.get("/events/{event_id}")
def get_security_event(event_id: int, db: Session = Depends(get_db)):
    """Retrieve specific security event"""
    event = db.query(SecurityEvent).filter(SecurityEvent.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return event.to_dict()

@router.get("/stats")
def get_security_stats(db: Session = Depends(get_db)):
    """Get security statistics"""
    from datetime import timedelta
    from sqlalchemy import func
    
    now = datetime.utcnow()
    day_ago = now - timedelta(days=1)
    
    total_events = db.query(SecurityEvent).count()
    events_24h = db.query(SecurityEvent).filter(SecurityEvent.timestamp >= day_ago).count()
    
    high_severity = db.query(SecurityEvent).filter(
        SecurityEvent.severity.in_(["high", "critical"]),
        SecurityEvent.timestamp >= day_ago
    ).count()
    
    threats_detected = db.query(SecurityEvent).filter(
        SecurityEvent.threat_indicators.isnot(None),
        SecurityEvent.timestamp >= day_ago
    ).count()
    
    event_types = db.query(
        SecurityEvent.event_type,
        func.count(SecurityEvent.id).label('count')
    ).filter(
        SecurityEvent.timestamp >= day_ago
    ).group_by(SecurityEvent.event_type).all()
    
    return {
        "total_events": total_events,
        "events_last_24h": events_24h,
        "high_severity_events": high_severity,
        "threats_detected": threats_detected,
        "events_by_type": {et: count for et, count in event_types}
    }
