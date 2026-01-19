from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import OperationalError
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from app.core.database import get_db
from app.core.mock_data import get_mock_reports
from app.models.security_event import SecurityEvent
from app.models.audit_log import AuditLog

router = APIRouter()

@router.get("/daily")
async def generate_daily_report(db: Optional[Session] = Depends(get_db)):
    """Generate daily security report"""
    if db is None:
        reports = get_mock_reports()
        return reports["daily"]
    
    try:
        today = datetime.utcnow().date()
        start_time = datetime.combine(today, datetime.min.time())
        end_time = datetime.combine(today, datetime.max.time())
        
        # Event statistics
        total_events = db.query(SecurityEvent).filter(
            SecurityEvent.created_at >= start_time,
            SecurityEvent.created_at <= end_time
        ).count()
        
        critical_events = db.query(SecurityEvent).filter(
            SecurityEvent.created_at >= start_time,
            SecurityEvent.created_at <= end_time,
            SecurityEvent.severity == "CRITICAL"
        ).count()
        
        resolved_events = db.query(SecurityEvent).filter(
            SecurityEvent.created_at >= start_time,
            SecurityEvent.created_at <= end_time,
            SecurityEvent.is_resolved == True
        ).count()
        
        # Top event types
        top_events = db.query(
            SecurityEvent.event_type,
            func.count(SecurityEvent.id).label('count')
        ).filter(
            SecurityEvent.created_at >= start_time,
            SecurityEvent.created_at <= end_time
        ).group_by(SecurityEvent.event_type).order_by(func.count(SecurityEvent.id).desc()).limit(5).all()
        
        return {
            "report_date": today.isoformat(),
            "total_events": total_events,
            "critical_events": critical_events,
            "resolved_events": resolved_events,
            "resolution_rate": round((resolved_events / total_events * 100) if total_events > 0 else 0, 2),
            "top_event_types": [
                {"event_type": item[0], "count": item[1]} for item in top_events
            ]
        }
    except (OperationalError, Exception) as e:
        print(f"Database error in generate_daily_report: {e}")
        reports = get_mock_reports()
        return reports["daily"]

@router.get("/weekly")
async def generate_weekly_report(db: Optional[Session] = Depends(get_db)):
    """Generate weekly security report"""
    if db is None:
        reports = get_mock_reports()
        return reports["weekly"]
    
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        
        # Daily breakdown
        daily_stats = []
        for i in range(7):
            day = start_date + timedelta(days=i)
            day_start = datetime.combine(day.date(), datetime.min.time())
            day_end = datetime.combine(day.date(), datetime.max.time())
            
            events = db.query(SecurityEvent).filter(
                SecurityEvent.created_at >= day_start,
                SecurityEvent.created_at <= day_end
            ).all()
            
            daily_stats.append({
                "date": day.strftime("%Y-%m-%d"),
                "total_events": len(events),
                "critical": sum(1 for e in events if e.severity == "CRITICAL"),
                "high": sum(1 for e in events if e.severity == "HIGH"),
                "medium": sum(1 for e in events if e.severity == "MEDIUM"),
                "low": sum(1 for e in events if e.severity == "LOW")
            })
        
        return {
            "report_period": {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d")
            },
            "daily_breakdown": daily_stats
        }
    except (OperationalError, Exception) as e:
        print(f"Database error in generate_weekly_report: {e}")
        reports = get_mock_reports()
        return reports["weekly"]

@router.get("/compliance")
async def generate_compliance_report(db: Optional[Session] = Depends(get_db)):
    """Generate compliance report"""
    if db is None:
        reports = get_mock_reports()
        return reports["compliance"]
    
    try:
        last_30_days = datetime.utcnow() - timedelta(days=30)
        
        # Security metrics
        total_events = db.query(SecurityEvent).filter(
            SecurityEvent.created_at >= last_30_days
        ).count()
        
        critical_unresolved = db.query(SecurityEvent).filter(
            SecurityEvent.severity == "CRITICAL",
            SecurityEvent.is_resolved == False,
            SecurityEvent.created_at >= last_30_days
        ).count()
        
        # Audit coverage
        total_audit_logs = db.query(AuditLog).filter(
            AuditLog.created_at >= last_30_days
        ).count()
        
        return {
            "report_period": "Last 30 days",
            "security_events": {
                "total": total_events,
                "critical_unresolved": critical_unresolved,
                "compliance_status": "PASS" if critical_unresolved == 0 else "REVIEW_REQUIRED"
            },
            "audit_coverage": {
                "total_logs": total_audit_logs,
                "coverage": "ADEQUATE" if total_audit_logs > 1000 else "NEEDS_IMPROVEMENT"
            },
            "generated_at": datetime.utcnow().isoformat()
        }
    except (OperationalError, Exception) as e:
        print(f"Database error in generate_compliance_report: {e}")
        reports = get_mock_reports()
        return reports["compliance"]
