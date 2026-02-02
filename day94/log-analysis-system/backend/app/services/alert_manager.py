from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.database import Alert, Anomaly, LogPattern
import hashlib

class AlertManager:
    """
    Intelligent alert manager with deduplication, severity scoring, and smart routing.
    """
    
    def __init__(self, db: Session, cooldown_seconds: int = 300):
        self.db = db
        self.cooldown_seconds = cooldown_seconds
    
    def calculate_severity_score(self, alert_type: str, metadata: Dict) -> Tuple[str, int]:
        """
        Calculate alert severity score (0-10) based on multiple factors.
        Returns (severity_level, score)
        """
        score = 0
        
        # Base score by type
        type_scores = {
            'critical_anomaly': 8,
            'pattern_spike': 6,
            'trend_degradation': 5,
            'new_pattern': 3
        }
        score += type_scores.get(alert_type, 3)
        
        # Adjust by anomaly magnitude
        if 'z_score' in metadata:
            z_score = metadata['z_score']
            if z_score > 5:
                score += 2
            elif z_score > 4:
                score += 1
        
        # Adjust by frequency
        if 'frequency' in metadata:
            freq = metadata['frequency']
            if freq > 1000:
                score += 2
            elif freq > 500:
                score += 1
        
        # Cap at 10
        score = min(score, 10)
        
        # Convert to severity level
        if score >= 8:
            severity = 'critical'
        elif score >= 6:
            severity = 'high'
        elif score >= 4:
            severity = 'medium'
        else:
            severity = 'low'
        
        return severity, score
    
    def check_duplicate(self, alert_type: str, source: str, 
                       related_entity_id: int) -> bool:
        """
        Check if similar alert exists within cooldown period.
        Prevents alert storms.
        """
        cooldown_start = datetime.utcnow() - timedelta(seconds=self.cooldown_seconds)
        
        existing = self.db.query(Alert).filter(
            Alert.alert_type == alert_type,
            Alert.source == source,
            Alert.related_entity_id == related_entity_id,
            Alert.timestamp >= cooldown_start,
            Alert.status.in_(['active', 'acknowledged'])
        ).first()
        
        return existing is not None
    
    def create_alert(self, alert_type: str, title: str, description: str,
                    source: str, related_entity_id: Optional[int] = None,
                    related_entity_type: Optional[str] = None,
                    metadata: Optional[Dict] = None) -> Optional[Alert]:
        """
        Create new alert with deduplication and severity scoring.
        """
        if metadata is None:
            metadata = {}
        
        # Check for duplicate
        if related_entity_id and self.check_duplicate(alert_type, source, related_entity_id):
            return None
        
        # Calculate severity
        severity, score = self.calculate_severity_score(alert_type, metadata)
        metadata['severity_score'] = score
        
        alert = Alert(
            alert_type=alert_type,
            severity=severity,
            title=title,
            description=description,
            source=source,
            related_entity_id=related_entity_id,
            related_entity_type=related_entity_type,
            extra_data=metadata
        )
        
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        
        return alert
    
    def create_anomaly_alert(self, anomaly: Anomaly) -> Optional[Alert]:
        """Create alert from detected anomaly"""
        title = f"Anomaly detected in {anomaly.metric_name}"
        description = (
            f"Detected {anomaly.anomaly_type} anomaly with Z-score {anomaly.z_score:.2f}. "
            f"Current value: {anomaly.metric_value:.2f}, "
            f"Baseline: {anomaly.baseline_mean:.2f} ± {anomaly.baseline_stddev:.2f}"
        )
        
        return self.create_alert(
            alert_type='anomaly',
            title=title,
            description=description,
            source=anomaly.source,
            related_entity_id=anomaly.id,
            related_entity_type='anomaly',
            metadata={
                'z_score': anomaly.z_score,
                'metric_name': anomaly.metric_name,
                'anomaly_type': anomaly.anomaly_type
            }
        )
    
    def create_pattern_alert(self, pattern: LogPattern, 
                            frequency_spike: bool = False) -> Optional[Alert]:
        """Create alert from pattern detection"""
        if frequency_spike:
            title = f"Frequency spike in pattern: {pattern.category}"
            alert_type = 'pattern_spike'
        else:
            title = f"New critical pattern detected: {pattern.category}"
            alert_type = 'new_pattern'
        
        description = (
            f"Pattern template: {pattern.pattern_template[:200]}... "
            f"Frequency: {pattern.frequency_count}, Severity: {pattern.severity}"
        )
        
        return self.create_alert(
            alert_type=alert_type,
            title=title,
            description=description,
            source='pattern_recognition',
            related_entity_id=pattern.id,
            related_entity_type='pattern',
            metadata={
                'frequency': pattern.frequency_count,
                'severity': pattern.severity,
                'is_critical': pattern.is_critical,
                'category': pattern.category
            }
        )
    
    def acknowledge_alert(self, alert_id: int) -> bool:
        """Acknowledge an active alert"""
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if alert and alert.status == 'active':
            alert.status = 'acknowledged'
            alert.acknowledged_at = datetime.utcnow()
            self.db.commit()
            return True
        return False
    
    def resolve_alert(self, alert_id: int) -> bool:
        """Resolve an acknowledged alert"""
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if alert and alert.status in ['active', 'acknowledged']:
            alert.status = 'resolved'
            alert.resolved_at = datetime.utcnow()
            self.db.commit()
            return True
        return False
    
    def get_active_alerts(self, severity: Optional[str] = None) -> List[Dict]:
        """Get all active alerts, optionally filtered by severity"""
        query = self.db.query(Alert).filter(
            Alert.status.in_(['active', 'acknowledged'])
        ).order_by(Alert.timestamp.desc())
        
        if severity:
            query = query.filter(Alert.severity == severity)
        
        alerts = query.limit(100).all()
        
        return [
            {
                'id': a.id,
                'timestamp': a.timestamp.isoformat(),
                'alert_type': a.alert_type,
                'severity': a.severity,
                'title': a.title,
                'description': a.description,
                'source': a.source,
                'status': a.status,
                'metadata': a.extra_data
            }
            for a in alerts
        ]
    
    def get_alert_statistics(self, hours: int = 24) -> Dict:
        """Get alert statistics for dashboard"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        total = self.db.query(Alert).filter(Alert.timestamp >= cutoff).count()
        active = self.db.query(Alert).filter(
            Alert.timestamp >= cutoff,
            Alert.status == 'active'
        ).count()
        resolved = self.db.query(Alert).filter(
            Alert.timestamp >= cutoff,
            Alert.status == 'resolved'
        ).count()
        
        by_severity = {}
        for severity in ['critical', 'high', 'medium', 'low']:
            count = self.db.query(Alert).filter(
                Alert.timestamp >= cutoff,
                Alert.severity == severity
            ).count()
            by_severity[severity] = count
        
        return {
            'total': total,
            'active': active,
            'resolved': resolved,
            'by_severity': by_severity
        }
