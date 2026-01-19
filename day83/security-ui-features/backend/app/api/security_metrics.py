from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import OperationalError
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from app.core.database import get_db
from app.core.mock_data import (
    get_mock_dashboard_metrics,
    get_mock_threat_distribution,
    get_mock_timeline
)
from app.models.security_event import SecurityEvent

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_metrics(db: Optional[Session] = Depends(get_db)):
    """Get real-time dashboard metrics"""
    if db is None:
        return get_mock_dashboard_metrics()
    
    try:
        now = datetime.utcnow()
        last_hour = now - timedelta(hours=1)
        last_24h = now - timedelta(days=1)
        last_7d = now - timedelta(days=7)
        
        # Active threats (unresolved high/critical)
        active_threats = db.query(SecurityEvent).filter(
            SecurityEvent.is_resolved == False,
            SecurityEvent.severity.in_(["HIGH", "CRITICAL"])
        ).count()
        
        # Events in last hour
        events_last_hour = db.query(SecurityEvent).filter(
            SecurityEvent.created_at >= last_hour
        ).count()
        
        # Average threat score (last 24h)
        avg_threat_score = db.query(func.avg(SecurityEvent.threat_score)).filter(
            SecurityEvent.created_at >= last_24h
        ).scalar() or 0
        
        # Event trend (last 7 days)
        event_trend = []
        for i in range(7):
            day_start = now - timedelta(days=i+1)
            day_end = now - timedelta(days=i)
            count = db.query(SecurityEvent).filter(
                SecurityEvent.created_at >= day_start,
                SecurityEvent.created_at < day_end
            ).count()
            event_trend.append({
                "date": day_start.strftime("%Y-%m-%d"),
                "count": count
            })
        
        return {
            "active_threats": active_threats,
            "events_last_hour": events_last_hour,
            "avg_threat_score": round(avg_threat_score, 2),
            "event_trend": list(reversed(event_trend)),
            "timestamp": now.isoformat()
        }
    except (OperationalError, Exception) as e:
        print(f"Database error in get_dashboard_metrics: {e}")
        return get_mock_dashboard_metrics()

@router.get("/threat-distribution")
async def get_threat_distribution(db: Optional[Session] = Depends(get_db)):
    """Get threat distribution by severity and type"""
    if db is None:
        return get_mock_threat_distribution()
    
    try:
        # Severity distribution
        severity_dist = db.query(
            SecurityEvent.severity,
            func.count(SecurityEvent.id).label('count')
        ).group_by(SecurityEvent.severity).all()
        
        # Event type distribution (top 10)
        type_dist = db.query(
            SecurityEvent.event_type,
            func.count(SecurityEvent.id).label('count')
        ).group_by(SecurityEvent.event_type).order_by(func.count(SecurityEvent.id).desc()).limit(10).all()
        
        return {
            "severity_distribution": [
                {"severity": item[0], "count": item[1]} for item in severity_dist
            ],
            "type_distribution": [
                {"event_type": item[0], "count": item[1]} for item in type_dist
            ]
        }
    except (OperationalError, Exception) as e:
        print(f"Database error in get_threat_distribution: {e}")
        return get_mock_threat_distribution()

@router.get("/timeline")
async def get_security_timeline(hours: int = 24, db: Optional[Session] = Depends(get_db)):
    """Get security event timeline"""
    if db is None:
        return get_mock_timeline(hours)
    
    try:
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Group events by hour
        timeline_data = []
        for i in range(hours):
            hour_start = start_time + timedelta(hours=i)
            hour_end = hour_start + timedelta(hours=1)
            
            events = db.query(SecurityEvent).filter(
                SecurityEvent.created_at >= hour_start,
                SecurityEvent.created_at < hour_end
            ).all()
            
            timeline_data.append({
                "timestamp": hour_start.isoformat(),
                "total_events": len(events),
                "critical": sum(1 for e in events if e.severity == "CRITICAL"),
                "high": sum(1 for e in events if e.severity == "HIGH"),
                "medium": sum(1 for e in events if e.severity == "MEDIUM"),
                "low": sum(1 for e in events if e.severity == "LOW")
            })
        
        return {"timeline": timeline_data}
    except (OperationalError, Exception) as e:
        print(f"Database error in get_security_timeline: {e}")
        return get_mock_timeline(hours)
