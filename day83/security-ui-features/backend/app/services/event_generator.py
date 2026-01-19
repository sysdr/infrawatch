import asyncio
import random
from datetime import datetime
from typing import List
import uuid
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.security_event import SecurityEvent

class SecurityEventGenerator:
    def __init__(self, ws_manager, db_gen=get_db):
        self.ws_manager = ws_manager
        self.db_gen = db_gen
        self.running = False
        
        self.event_types = [
            "authentication_failed", "authentication_success", "authorization_denied",
            "suspicious_activity", "brute_force_attempt", "sql_injection_attempt",
            "xss_attempt", "rate_limit_exceeded", "unusual_access_pattern",
            "privilege_escalation", "data_exfiltration", "malware_detected"
        ]
        
        self.severities = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        self.sources = ["web_app", "api_server", "mobile_app", "admin_panel", "internal_service"]
        self.users = ["user_001", "user_002", "user_003", "admin_001", "service_account"]
        self.ips = [
            "192.168.1.100", "10.0.0.50", "172.16.0.25",
            "203.0.113.45", "198.51.100.78", "192.0.2.123"
        ]
    
    async def generate_events(self):
        """Generate random security events for demonstration"""
        self.running = True
        print("Security event generator started")
        
        while self.running:
            try:
                # Generate 1-3 events per interval
                num_events = random.randint(1, 3)
                
                # Get database session
                db_gen = self.db_gen()
                db = next(db_gen)
                
                try:
                    for _ in range(num_events):
                        event_dict = self._create_random_event()
                        # Broadcast via WebSocket
                        await self.ws_manager.broadcast_event(event_dict)
                        
                        # Persist to database
                        db_event = SecurityEvent(
                            event_id=event_dict["event_id"],
                            event_type=event_dict["event_type"],
                            severity=event_dict["severity"],
                            source=event_dict["source"],
                            destination=None,
                            user_id=event_dict["user_id"],
                            ip_address=event_dict["ip_address"],
                            user_agent=event_dict["metadata"].get("user_agent"),
                            description=event_dict["description"],
                            event_metadata=event_dict["metadata"],
                            threat_score=event_dict["threat_score"],
                            is_resolved=False
                        )
                        db.add(db_event)
                    
                    db.commit()
                finally:
                    db.close()
                
                # Wait 2-5 seconds between batches
                await asyncio.sleep(random.uniform(2, 5))
                
            except Exception as e:
                print(f"Error generating events: {e}")
                import traceback
                traceback.print_exc()
                await asyncio.sleep(5)
    
    def _create_random_event(self) -> dict:
        """Create a random security event"""
        event_type = random.choice(self.event_types)
        severity = random.choices(
            self.severities,
            weights=[50, 30, 15, 5],  # More low/medium, fewer critical
            k=1
        )[0]
        
        # Threat score correlates with severity
        threat_score_ranges = {
            "LOW": (1, 30),
            "MEDIUM": (31, 60),
            "HIGH": (61, 85),
            "CRITICAL": (86, 100)
        }
        min_score, max_score = threat_score_ranges[severity]
        threat_score = random.randint(min_score, max_score)
        
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "severity": severity,
            "source": random.choice(self.sources),
            "user_id": random.choice(self.users),
            "ip_address": random.choice(self.ips),
            "description": self._get_description(event_type, severity),
            "threat_score": threat_score,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "location": random.choice(["US-EAST", "EU-WEST", "ASIA-PACIFIC"]),
                "session_id": str(uuid.uuid4())[:8]
            }
        }
        
        return event
    
    def _get_description(self, event_type: str, severity: str) -> str:
        """Generate description based on event type"""
        descriptions = {
            "authentication_failed": f"{severity}: Failed login attempt detected",
            "authentication_success": "User successfully authenticated",
            "authorization_denied": f"{severity}: Unauthorized access attempt to protected resource",
            "suspicious_activity": f"{severity}: Unusual behavior pattern detected",
            "brute_force_attempt": f"{severity}: Multiple failed login attempts from single source",
            "sql_injection_attempt": f"{severity}: SQL injection attack detected and blocked",
            "xss_attempt": f"{severity}: Cross-site scripting attempt blocked",
            "rate_limit_exceeded": "API rate limit exceeded",
            "unusual_access_pattern": f"{severity}: Abnormal access pattern detected",
            "privilege_escalation": f"{severity}: Unauthorized privilege escalation attempt",
            "data_exfiltration": f"{severity}: Suspicious data transfer detected",
            "malware_detected": f"{severity}: Malicious code detected and quarantined"
        }
        
        return descriptions.get(event_type, f"{severity}: Security event detected")
    
    def stop(self):
        """Stop event generation"""
        self.running = False
        print("Security event generator stopped")
