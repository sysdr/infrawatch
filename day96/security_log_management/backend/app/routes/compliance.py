from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.services.compliance_reporter import ComplianceReporter
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/reports/gdpr")
def generate_gdpr_report(
    days: int = Query(90, le=365),
    db: Session = Depends(get_db)
):
    """Generate GDPR compliance report"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    report = ComplianceReporter.generate_gdpr_report(db, start_date, end_date)
    return report

@router.get("/reports/soc2")
def generate_soc2_report(
    days: int = Query(90, le=365),
    db: Session = Depends(get_db)
):
    """Generate SOC2 compliance report"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    report = ComplianceReporter.generate_soc2_report(db, start_date, end_date)
    return report

@router.get("/verify/integrity")
def verify_audit_integrity(db: Session = Depends(get_db)):
    """Verify audit trail integrity"""
    report = ComplianceReporter.generate_audit_trail_verification(db)
    return report

@router.get("/metrics")
def get_compliance_metrics(db: Session = Depends(get_db)):
    """Get compliance metrics dashboard"""
    from app.models.security_event import SecurityEvent
    from app.models.incident import Incident
    from datetime import timedelta
    
    now = datetime.utcnow()
    thirty_days_ago = now - timedelta(days=30)
    
    # Authentication metrics
    total_auth = db.query(SecurityEvent).filter(
        SecurityEvent.event_type == "authentication",
        SecurityEvent.timestamp >= thirty_days_ago
    ).count()
    
    failed_auth = db.query(SecurityEvent).filter(
        SecurityEvent.event_type == "authentication",
        SecurityEvent.result == "failure",
        SecurityEvent.timestamp >= thirty_days_ago
    ).count()
    
    # Incident metrics
    critical_incidents = db.query(Incident).filter(
        Incident.severity == "critical",
        Incident.created_at >= thirty_days_ago
    ).count()
    
    resolved_incidents = db.query(Incident).filter(
        Incident.status == "resolved",
        Incident.created_at >= thirty_days_ago
    ).count()
    
    total_incidents = db.query(Incident).filter(
        Incident.created_at >= thirty_days_ago
    ).count()
    
    return {
        "period": "last_30_days",
        "authentication": {
            "total_attempts": total_auth,
            "failed_attempts": failed_auth,
            "failure_rate": round((failed_auth / total_auth * 100) if total_auth > 0 else 0, 2)
        },
        "incidents": {
            "total": total_incidents,
            "critical": critical_incidents,
            "resolved": resolved_incidents,
            "resolution_rate": round((resolved_incidents / total_incidents * 100) if total_incidents > 0 else 0, 2)
        },
        "compliance_status": "compliant" if total_auth == 0 or (failed_auth / total_auth < 0.05) else "review_required"
    }
