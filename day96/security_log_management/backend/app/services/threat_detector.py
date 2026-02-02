from typing import Dict, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.security_event import SecurityEvent
from app.utils.redis_client import redis_client, increment_counter, cache_get, cache_set
import json

class ThreatDetector:
    
    # Threat detection rules
    RULES = {
        "brute_force": {"threshold": 5, "window": 300},  # 5 failures in 5 minutes
        "anomalous_access": {"threshold": 3.0},  # Anomaly score > 3.0
        "privilege_escalation": {"threshold": 3, "window": 3600},  # 3 attempts in 1 hour
        "data_exfiltration": {"threshold": 1000, "window": 3600},  # 1000 records in 1 hour
    }
    
    @staticmethod
    def detect_brute_force(user_id: str, ip_address: str, event_type: str) -> Dict:
        """Detect brute force authentication attempts"""
        if event_type not in ["authentication", "login_attempt"]:
            return {"threat_detected": False}
        
        key = f"auth_failures:{ip_address}"
        count = increment_counter(key, window=300)
        
        if count >= ThreatDetector.RULES["brute_force"]["threshold"]:
            return {
                "threat_detected": True,
                "threat_type": "brute_force",
                "severity": "high",
                "details": f"Multiple failed login attempts from {ip_address}",
                "count": count
            }
        
        return {"threat_detected": False, "count": count}
    
    @staticmethod
    def calculate_anomaly_score(
        db: Session,
        user_id: str,
        event_type: str,
        current_action: str
    ) -> float:
        """Calculate anomaly score based on user behavior baseline"""
        
        # Get user baseline from cache
        baseline_key = f"baseline:{user_id}:{event_type}"
        baseline = cache_get(baseline_key)
        
        if not baseline:
            # Calculate baseline from historical data
            week_ago = datetime.utcnow() - timedelta(days=7)
            events = db.query(SecurityEvent).filter(
                SecurityEvent.user_id == user_id,
                SecurityEvent.event_type == event_type,
                SecurityEvent.timestamp >= week_ago
            ).all()
            
            if len(events) < 10:  # Not enough data
                return 0.0
            
            # Calculate average events per day
            avg_per_day = len(events) / 7
            baseline = {"avg_per_day": avg_per_day, "common_actions": {}}
            
            # Cache baseline
            cache_set(baseline_key, baseline, expire=86400)
        
        # Check current day activity
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_count = db.query(SecurityEvent).filter(
            SecurityEvent.user_id == user_id,
            SecurityEvent.event_type == event_type,
            SecurityEvent.timestamp >= today_start
        ).count()
        
        # Calculate anomaly score
        avg = baseline.get("avg_per_day", 1)
        if today_count > avg * 3:  # More than 3x normal
            return min((today_count / avg) - 1, 5.0)
        
        return 0.0
    
    @staticmethod
    def detect_privilege_escalation(db: Session, user_id: str) -> Dict:
        """Detect privilege escalation attempts"""
        hour_ago = datetime.utcnow() - timedelta(hours=1)
        
        escalation_events = db.query(SecurityEvent).filter(
            SecurityEvent.user_id == user_id,
            SecurityEvent.event_type == "authorization",
            SecurityEvent.result == "failure",
            SecurityEvent.timestamp >= hour_ago
        ).count()
        
        if escalation_events >= ThreatDetector.RULES["privilege_escalation"]["threshold"]:
            return {
                "threat_detected": True,
                "threat_type": "privilege_escalation",
                "severity": "critical",
                "details": f"Multiple authorization failures for user {user_id}",
                "count": escalation_events
            }
        
        return {"threat_detected": False}
    
    @staticmethod
    def detect_data_exfiltration(db: Session, user_id: str) -> Dict:
        """Detect potential data exfiltration"""
        hour_ago = datetime.utcnow() - timedelta(hours=1)
        
        data_access_events = db.query(SecurityEvent).filter(
            SecurityEvent.user_id == user_id,
            SecurityEvent.event_type == "data_access",
            SecurityEvent.timestamp >= hour_ago
        ).count()
        
        if data_access_events >= ThreatDetector.RULES["data_exfiltration"]["threshold"]:
            return {
                "threat_detected": True,
                "threat_type": "data_exfiltration",
                "severity": "critical",
                "details": f"Unusual volume of data access by user {user_id}",
                "count": data_access_events
            }
        
        return {"threat_detected": False}
    
    @staticmethod
    def correlate_events(db: Session, correlation_id: str, time_window: int = 900) -> List[Dict]:
        """Correlate related security events"""
        cutoff = datetime.utcnow() - timedelta(seconds=time_window)
        
        events = db.query(SecurityEvent).filter(
            SecurityEvent.correlation_id == correlation_id,
            SecurityEvent.timestamp >= cutoff
        ).order_by(SecurityEvent.timestamp).all()
        
        return [event.to_dict() for event in events]
