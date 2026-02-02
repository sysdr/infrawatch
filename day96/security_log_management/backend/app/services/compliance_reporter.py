from typing import Dict, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.security_event import SecurityEvent
from app.models.incident import Incident

class ComplianceReporter:
    
    @staticmethod
    def generate_gdpr_report(db: Session, start_date: datetime, end_date: datetime) -> Dict:
        """Generate GDPR compliance report"""
        
        # Data access events
        data_access = db.query(SecurityEvent).filter(
            SecurityEvent.event_type == "data_access",
            SecurityEvent.timestamp >= start_date,
            SecurityEvent.timestamp <= end_date
        ).all()
        
        # Group by user and resource
        access_by_user = {}
        for event in data_access:
            user_id = event.user_id or "unknown"
            if user_id not in access_by_user:
                access_by_user[user_id] = []
            access_by_user[user_id].append({
                "resource": event.resource,
                "action": event.action,
                "timestamp": event.timestamp.isoformat()
            })
        
        return {
            "report_type": "GDPR_DATA_ACCESS",
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "total_access_events": len(data_access),
            "unique_users": len(access_by_user),
            "access_by_user": access_by_user,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def generate_soc2_report(db: Session, start_date: datetime, end_date: datetime) -> Dict:
        """Generate SOC2 compliance report"""
        
        # Authentication events
        auth_events = db.query(
            SecurityEvent.result,
            func.count(SecurityEvent.id).label('count')
        ).filter(
            SecurityEvent.event_type.in_(["authentication", "login_attempt"]),
            SecurityEvent.timestamp >= start_date,
            SecurityEvent.timestamp <= end_date
        ).group_by(SecurityEvent.result).all()
        
        # Authorization events
        authz_events = db.query(SecurityEvent).filter(
            SecurityEvent.event_type == "authorization",
            SecurityEvent.result == "failure",
            SecurityEvent.timestamp >= start_date,
            SecurityEvent.timestamp <= end_date
        ).count()
        
        # Incidents
        incidents = db.query(Incident).filter(
            Incident.created_at >= start_date,
            Incident.created_at <= end_date
        ).all()
        
        return {
            "report_type": "SOC2_ACCESS_CONTROL",
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "authentication_summary": {
                result: count for result, count in auth_events
            },
            "failed_authorization_attempts": authz_events,
            "security_incidents": {
                "total": len(incidents),
                "by_severity": {
                    "critical": len([i for i in incidents if i.severity == "critical"]),
                    "high": len([i for i in incidents if i.severity == "high"]),
                    "medium": len([i for i in incidents if i.severity == "medium"]),
                    "low": len([i for i in incidents if i.severity == "low"])
                },
                "resolved": len([i for i in incidents if i.status == "resolved"])
            },
            "generated_at": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def generate_audit_trail_verification(db: Session) -> Dict:
        """Verify audit trail integrity"""
        
        # Get all events ordered by timestamp
        events = db.query(SecurityEvent).order_by(SecurityEvent.timestamp).limit(1000).all()
        
        integrity_violations = []
        for i, event in enumerate(events):
            if i > 0:
                expected_prev_hash = events[i-1].event_hash
                if event.previous_hash != expected_prev_hash:
                    integrity_violations.append({
                        "event_id": event.id,
                        "expected": expected_prev_hash,
                        "actual": event.previous_hash
                    })
        
        return {
            "report_type": "AUDIT_TRAIL_VERIFICATION",
            "total_events_checked": len(events),
            "integrity_violations": len(integrity_violations),
            "violations": integrity_violations,
            "status": "PASS" if len(integrity_violations) == 0 else "FAIL",
            "generated_at": datetime.utcnow().isoformat()
        }
