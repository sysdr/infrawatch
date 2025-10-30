from sqlalchemy.orm import Session
from models.notification_preference import (
    NotificationPreference, ChannelPreference, QuietHours, 
    EscalationRule, NotificationSubscription, NotificationCategory, NotificationPriority
)
from datetime import datetime, time
import pytz
from typing import Dict, List, Any

class PreferenceService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_user_preference(self, user_id: int, global_quiet_hours_enabled: bool = False):
        """Create default preferences for a user"""
        preference = NotificationPreference(
            user_id=user_id,
            global_quiet_hours_enabled=global_quiet_hours_enabled
        )
        self.db.add(preference)
        self.db.commit()
        self.db.refresh(preference)
        
        # Create default channel preferences
        default_channels = [
            {"channel": "email", "priority_score": 80, "is_enabled": True},
            {"channel": "push", "priority_score": 70, "is_enabled": True},
            {"channel": "sms", "priority_score": 60, "is_enabled": False},
            {"channel": "in_app", "priority_score": 90, "is_enabled": True},
        ]
        
        for channel_data in default_channels:
            channel_pref = ChannelPreference(
                preference_id=preference.id,
                **channel_data
            )
            self.db.add(channel_pref)
        
        self.db.commit()
        return preference
    
    def get_user_preferences(self, user_id: int):
        """Get all preferences for a user"""
        return self.db.query(NotificationPreference).filter(
            NotificationPreference.user_id == user_id
        ).first()
    
    def update_quiet_hours(self, user_id: int, quiet_hours_data: Dict):
        """Update quiet hours settings"""
        preference = self.get_user_preferences(user_id)
        if not preference:
            raise ValueError("User preferences not found")
        
        # Remove existing quiet hours
        self.db.query(QuietHours).filter(
            QuietHours.preference_id == preference.id
        ).delete()
        
        # Create new quiet hours
        start_time = datetime.strptime(quiet_hours_data["start_time"], "%H:%M").time()
        end_time = datetime.strptime(quiet_hours_data["end_time"], "%H:%M").time()
        
        quiet_hours = QuietHours(
            preference_id=preference.id,
            start_time=start_time,
            end_time=end_time,
            timezone=quiet_hours_data.get("timezone", "UTC"),
            days_of_week=quiet_hours_data.get("days_of_week", [0,1,2,3,4,5,6]),
            exceptions=quiet_hours_data.get("exceptions", ["security"])
        )
        
        self.db.add(quiet_hours)
        preference.global_quiet_hours_enabled = True
        self.db.commit()
        return quiet_hours
    
    def update_channel_preferences(self, user_id: int, channels_data: List[Dict]):
        """Update channel preferences"""
        preference = self.get_user_preferences(user_id)
        if not preference:
            raise ValueError("User preferences not found")
        
        # Remove existing channel preferences
        self.db.query(ChannelPreference).filter(
            ChannelPreference.preference_id == preference.id
        ).delete()
        
        # Create new channel preferences
        for channel_data in channels_data:
            channel_pref = ChannelPreference(
                preference_id=preference.id,
                **channel_data
            )
            self.db.add(channel_pref)
        
        self.db.commit()
        return channels_data
    
    def create_escalation_rule(self, user_id: int, rule_data: Dict):
        """Create escalation rule"""
        preference = self.get_user_preferences(user_id)
        if not preference:
            raise ValueError("User preferences not found")
        
        rule = EscalationRule(
            preference_id=preference.id,
            category=getattr(NotificationCategory, rule_data["category"].upper()),
            priority_threshold=getattr(NotificationPriority, rule_data["priority_threshold"].upper()),
            escalation_delay_minutes=rule_data.get("escalation_delay_minutes", 15),
            escalation_channels=rule_data.get("escalation_channels", []),
            escalation_contacts=rule_data.get("escalation_contacts", []),
            max_attempts=rule_data.get("max_attempts", 3)
        )
        
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        return rule
    
    def get_escalation_rules(self, user_id: int):
        """Get all escalation rules for a user"""
        preference = self.get_user_preferences(user_id)
        if not preference:
            return []
        
        return self.db.query(EscalationRule).filter(
            EscalationRule.preference_id == preference.id
        ).all()
    
    def should_send_notification(self, user_id: int, notification_data: Dict) -> Dict[str, Any]:
        """Determine if notification should be sent based on user preferences"""
        preference = self.get_user_preferences(user_id)
        if not preference or not preference.is_enabled:
            return {"should_send": False, "reason": "Notifications disabled"}
        
        # Check quiet hours
        if self._is_in_quiet_hours(preference, notification_data):
            if not self._has_quiet_hours_exception(preference, notification_data):
                return {"should_send": False, "reason": "In quiet hours"}
        
        # Determine channels based on preferences
        channels = self._get_preferred_channels(preference, notification_data)
        
        return {
            "should_send": True,
            "channels": channels,
            "escalation_rules": self._get_applicable_escalation_rules(preference, notification_data)
        }
    
    def _is_in_quiet_hours(self, preference: NotificationPreference, notification_data: Dict) -> bool:
        """Check if current time is within user's quiet hours"""
        if not preference.global_quiet_hours_enabled:
            return False
        
        quiet_hours = self.db.query(QuietHours).filter(
            QuietHours.preference_id == preference.id
        ).first()
        
        if not quiet_hours:
            return False
        
        # Get current time in user's timezone
        user_tz = pytz.timezone(quiet_hours.timezone)
        current_time = datetime.now(user_tz).time()
        current_weekday = datetime.now(user_tz).weekday()
        
        # Check if today is included in quiet hours days
        if current_weekday not in quiet_hours.days_of_week:
            return False
        
        # Check if current time is within quiet hours range
        if quiet_hours.start_time <= quiet_hours.end_time:
            # Same day range (e.g., 22:00 to 08:00 next day)
            return quiet_hours.start_time <= current_time <= quiet_hours.end_time
        else:
            # Crosses midnight (e.g., 22:00 to 08:00)
            return current_time >= quiet_hours.start_time or current_time <= quiet_hours.end_time
    
    def _has_quiet_hours_exception(self, preference: NotificationPreference, notification_data: Dict) -> bool:
        """Check if notification category has quiet hours exception"""
        quiet_hours = self.db.query(QuietHours).filter(
            QuietHours.preference_id == preference.id
        ).first()
        
        if not quiet_hours or not quiet_hours.exceptions:
            return False
        
        category = notification_data.get("category", "").lower()
        priority = notification_data.get("priority", "").lower()
        
        return category in quiet_hours.exceptions or priority in quiet_hours.exceptions
    
    def _get_preferred_channels(self, preference: NotificationPreference, notification_data: Dict) -> List[str]:
        """Get preferred channels based on user preferences and notification priority"""
        channel_prefs = self.db.query(ChannelPreference).filter(
            ChannelPreference.preference_id == preference.id,
            ChannelPreference.is_enabled == True
        ).order_by(ChannelPreference.priority_score.desc()).all()
        
        priority = notification_data.get("priority", "medium")
        
        # For high/critical priority, include more channels
        if priority in ["high", "critical"]:
            return [cp.channel for cp in channel_prefs if cp.priority_score >= 60]
        else:
            return [cp.channel for cp in channel_prefs if cp.priority_score >= 70]
    
    def _get_applicable_escalation_rules(self, preference: NotificationPreference, notification_data: Dict) -> List[Dict]:
        """Get applicable escalation rules for this notification"""
        category = notification_data.get("category", "").upper()
        priority = notification_data.get("priority", "").upper()
        
        rules = self.db.query(EscalationRule).filter(
            EscalationRule.preference_id == preference.id
        ).all()
        
        applicable_rules = []
        for rule in rules:
            if (rule.category.value.upper() == category and 
                getattr(NotificationPriority, priority, NotificationPriority.MEDIUM).value == rule.priority_threshold.value):
                applicable_rules.append({
                    "delay_minutes": rule.escalation_delay_minutes,
                    "channels": rule.escalation_channels,
                    "contacts": rule.escalation_contacts,
                    "max_attempts": rule.max_attempts
                })
        
        return applicable_rules
    
    def test_notification_processing(self, user_id: int, notification_data: Dict):
        """Test notification processing without sending"""
        result = self.should_send_notification(user_id, notification_data)
        
        return {
            "input": notification_data,
            "user_id": user_id,
            "processing_result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
