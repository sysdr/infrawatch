from typing import Dict, List
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.incident import Incident
import uuid

class IncidentResponder:
    
    @staticmethod
    def create_incident(
        db: Session,
        threat_data: Dict,
        related_events: List[Dict]
    ) -> Incident:
        """Create security incident from threat detection"""
        
        incident_id = f"INC-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        incident = Incident(
            incident_id=incident_id,
            title=f"{threat_data.get('threat_type', 'Security')} Threat Detected",
            description=threat_data.get('details', 'Security threat detected'),
            severity=threat_data.get('severity', 'medium'),
            status="open",
            incident_type=threat_data.get('threat_type', 'unknown'),
            affected_users=[event.get('user_id') for event in related_events if event.get('user_id')],
            affected_resources=[event.get('resource') for event in related_events if event.get('resource')],
            detection_method="automated",
            confidence_score=threat_data.get('confidence_score', 80),
            auto_response_taken=False,
            response_actions=[],
            related_events=[event.get('id') for event in related_events]
        )
        
        db.add(incident)
        db.commit()
        db.refresh(incident)
        
        # Auto-response based on severity
        if incident.severity == "critical":
            IncidentResponder.execute_auto_response(db, incident)
        
        return incident
    
    @staticmethod
    def execute_auto_response(db: Session, incident: Incident):
        """Execute automated incident response actions"""
        actions = []
        
        if incident.incident_type == "brute_force":
            actions.append({
                "action": "block_ip",
                "target": incident.affected_users,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        elif incident.incident_type == "privilege_escalation":
            actions.append({
                "action": "suspend_account",
                "target": incident.affected_users,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        elif incident.incident_type == "data_exfiltration":
            actions.append({
                "action": "revoke_access",
                "target": incident.affected_users,
                "timestamp": datetime.utcnow().isoformat()
            })
            actions.append({
                "action": "alert_security_team",
                "severity": "critical",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        incident.auto_response_taken = True
        incident.response_actions = actions
        db.commit()
    
    @staticmethod
    def update_incident_status(
        db: Session,
        incident_id: str,
        status: str,
        resolution_notes: str = None
    ) -> Incident:
        """Update incident status"""
        incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
        
        if incident:
            incident.status = status
            incident.updated_at = datetime.utcnow()
            
            if status == "resolved" and resolution_notes:
                incident.resolved_at = datetime.utcnow()
                incident.resolution_notes = resolution_notes
            
            db.commit()
            db.refresh(incident)
        
        return incident
