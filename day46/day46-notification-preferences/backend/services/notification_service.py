from sqlalchemy.orm import Session
from .preference_service import PreferenceService
from datetime import datetime

class NotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.preference_service = PreferenceService(db)
    
    def process_notification(self, notification_data: dict):
        """Process notification through preference system"""
        user_id = notification_data["user_id"]
        
        # Check user preferences
        preference_result = self.preference_service.should_send_notification(
            user_id, notification_data
        )
        
        if not preference_result["should_send"]:
            return {
                "status": "blocked",
                "reason": preference_result["reason"],
                "notification": notification_data
            }
        
        # Simulate sending notification
        return {
            "status": "sent",
            "channels": preference_result["channels"],
            "escalation_rules": preference_result.get("escalation_rules", []),
            "notification": notification_data,
            "processed_at": datetime.utcnow().isoformat()
        }
    
    def simulate_notification_processing(self, notification_data: dict):
        """Simulate notification processing for testing"""
        return self.preference_service.test_notification_processing(
            notification_data["user_id"], notification_data
        )
