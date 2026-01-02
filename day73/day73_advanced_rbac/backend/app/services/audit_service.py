from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Optional
from ..models.permission_models import AuditEvent

class AuditService:
    def __init__(self, db: Session):
        self.db = db
    
    def log_event(self, subject_type: str, subject_id: str, action: str,
                  resource_type: str, resource_id: str, decision: str,
                  reason: str, policy_matched: str, context: Dict = None):
        """Log audit event."""
        event = AuditEvent(
            timestamp=datetime.utcnow(),
            subject_type=subject_type,
            subject_id=subject_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            decision=decision,
            reason=reason,
            policy_matched=policy_matched,
            context=context or {}
        )
        
        self.db.add(event)
        self.db.commit()
        
        return event
    
    def get_recent_events(self, limit: int = 100, filters: Dict = None):
        """Get recent audit events with optional filters."""
        query = self.db.query(AuditEvent).order_by(AuditEvent.timestamp.desc())
        
        if filters:
            if 'subject_id' in filters:
                query = query.filter(AuditEvent.subject_id == filters['subject_id'])
            if 'resource_type' in filters:
                query = query.filter(AuditEvent.resource_type == filters['resource_type'])
            if 'decision' in filters:
                query = query.filter(AuditEvent.decision == filters['decision'])
        
        return query.limit(limit).all()
    
    def get_event_stats(self, time_range_hours: int = 24) -> Dict:
        """Get audit event statistics."""
        from sqlalchemy import func
        from datetime import timedelta
        
        cutoff = datetime.utcnow() - timedelta(hours=time_range_hours)
        
        total_checks = self.db.query(func.count(AuditEvent.id)).filter(
            AuditEvent.timestamp >= cutoff
        ).scalar()
        
        allowed = self.db.query(func.count(AuditEvent.id)).filter(
            AuditEvent.timestamp >= cutoff,
            AuditEvent.decision == 'allowed'
        ).scalar()
        
        denied = self.db.query(func.count(AuditEvent.id)).filter(
            AuditEvent.timestamp >= cutoff,
            AuditEvent.decision == 'denied'
        ).scalar()
        
        return {
            'total_checks': total_checks or 0,
            'allowed': allowed or 0,
            'denied': denied or 0,
            'deny_rate': (denied / total_checks * 100) if total_checks else 0
        }
