from typing import Dict, Any
from datetime import datetime
from .models import Event

class MessageFormatter:
    def __init__(self):
        self.version = "1.0.0"
    
    def format_message(self, event: Event) -> Dict[str, Any]:
        """Format event into standardized message structure"""
        return {
            "version": self.version,
            "type": event.type.value,
            "id": event.id,
            "timestamp": event.timestamp.isoformat(),
            "payload": event.payload,
            "metadata": {
                "client_id": event.client_id,
                "event_version": event.version,
                "server_timestamp": datetime.utcnow().isoformat()
            }
        }
    
    def format_acknowledgment(self, event: Event, conflict_detected: bool = False) -> Dict[str, Any]:
        """Format acknowledgment message"""
        return {
            "type": "ack",
            "id": event.id,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "received",
            "version": event.version,
            "conflict_detected": conflict_detected
        }
    
    def validate_message(self, message: Dict[str, Any]) -> bool:
        """Validate message structure"""
        required_fields = ["type", "payload"]
        return all(field in message for field in required_fields)
