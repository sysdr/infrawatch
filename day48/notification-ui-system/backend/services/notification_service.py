from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid
import json
import logging
from models.notification import (
    Notification, NotificationPreference, NotificationHistory,
    NotificationType, NotificationPriority, NotificationChannel
)

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        # In-memory storage for demo (replace with database in production)
        self.notifications: Dict[str, Notification] = {}
        self.preferences: Dict[str, List[NotificationPreference]] = {}
        self.history: List[NotificationHistory] = []
        self.initialized = False

    async def initialize(self):
        """Initialize service with default data"""
        if not self.initialized:
            # Create default preferences for demo user
            await self.create_default_preferences("demo-user")
            self.initialized = True
            logger.info("Notification service initialized")

    async def create_default_preferences(self, user_id: str):
        """Create default notification preferences for a user"""
        default_preferences = [
            NotificationPreference(
                id=str(uuid.uuid4()),
                userId=user_id,
                channel=NotificationChannel.EMAIL,
                enabled=True,
                types=[NotificationType.ERROR, NotificationType.WARNING],
                priorities=[NotificationPriority.HIGH, NotificationPriority.CRITICAL]
            ),
            NotificationPreference(
                id=str(uuid.uuid4()),
                userId=user_id,
                channel=NotificationChannel.PUSH,
                enabled=True,
                types=[NotificationType.SUCCESS, NotificationType.INFO, NotificationType.ERROR],
                priorities=[NotificationPriority.MEDIUM, NotificationPriority.HIGH, NotificationPriority.CRITICAL]
            ),
            NotificationPreference(
                id=str(uuid.uuid4()),
                userId=user_id,
                channel=NotificationChannel.SMS,
                enabled=False,
                types=[NotificationType.ERROR],
                priorities=[NotificationPriority.CRITICAL]
            )
        ]
        
        self.preferences[user_id] = default_preferences

    async def create_notification(self, notification_data: Dict[str, Any]) -> Notification:
        """Create a new notification"""
        notification = Notification(
            id=str(uuid.uuid4()),
            title=notification_data["title"],
            message=notification_data["message"],
            type=NotificationType(notification_data["type"]),
            priority=NotificationPriority(notification_data["priority"]),
            timestamp=datetime.now(),
            userId=notification_data["userId"],
            data=notification_data.get("data")
        )
        
        self.notifications[notification.id] = notification
        
        # Add to history
        await self.add_history_entry(
            notification.id, "created", {"source": "api"}
        )
        
        logger.info(f"Created notification {notification.id}")
        return notification

    async def get_notifications(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get notifications for a user"""
        user_notifications = [
            notification for notification in self.notifications.values()
            if notification.userId == user_id
        ]
        
        # Sort by timestamp (newest first)
        user_notifications.sort(key=lambda x: x.timestamp, reverse=True)
        
        return [
            {
                "id": notif.id,
                "title": notif.title,
                "message": notif.message,
                "type": notif.type.value,
                "priority": notif.priority.value,
                "timestamp": notif.timestamp.isoformat(),
                "acknowledged": notif.acknowledged,
                "data": notif.data
            }
            for notif in user_notifications[:limit]
        ]

    async def acknowledge_notification(self, notification_id: str):
        """Mark notification as acknowledged"""
        if notification_id in self.notifications:
            self.notifications[notification_id].acknowledged = True
            await self.add_history_entry(
                notification_id, "acknowledged", {"timestamp": datetime.now().isoformat()}
            )
            logger.info(f"Acknowledged notification {notification_id}")

    async def get_preferences(self, user_id: str) -> List[Dict[str, Any]]:
        """Get notification preferences for a user"""
        if user_id not in self.preferences:
            await self.create_default_preferences(user_id)
        
        preferences = self.preferences[user_id]
        return [
            {
                "id": pref.id,
                "channel": pref.channel.value,
                "enabled": pref.enabled,
                "types": [t.value for t in pref.types],
                "priorities": [p.value for p in pref.priorities],
                "settings": pref.settings or {}
            }
            for pref in preferences
        ]

    async def update_preference(self, user_id: str, preference_id: str, update_data: Dict[str, Any]):
        """Update notification preference"""
        if user_id in self.preferences:
            for pref in self.preferences[user_id]:
                if pref.id == preference_id:
                    pref.enabled = update_data.get("enabled", pref.enabled)
                    if "types" in update_data:
                        pref.types = [NotificationType(t) for t in update_data["types"]]
                    if "priorities" in update_data:
                        pref.priorities = [NotificationPriority(p) for p in update_data["priorities"]]
                    if "settings" in update_data:
                        pref.settings = update_data["settings"]
                    
                    logger.info(f"Updated preference {preference_id} for user {user_id}")
                    break

    async def get_history(self, user_id: str, notification_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get notification history"""
        history_items = self.history
        
        if notification_id:
            history_items = [h for h in history_items if h.notificationId == notification_id]
        
        # Filter by user notifications
        user_notification_ids = [
            notif.id for notif in self.notifications.values()
            if notif.userId == user_id
        ]
        
        history_items = [
            h for h in history_items
            if h.notificationId in user_notification_ids
        ]
        
        return [
            {
                "id": h.id,
                "notificationId": h.notificationId,
                "action": h.action,
                "timestamp": h.timestamp.isoformat(),
                "details": h.details
            }
            for h in sorted(history_items, key=lambda x: x.timestamp, reverse=True)
        ]

    async def add_history_entry(self, notification_id: str, action: str, details: Dict[str, Any]):
        """Add entry to notification history"""
        history_entry = NotificationHistory(
            id=str(uuid.uuid4()),
            notificationId=notification_id,
            action=action,
            timestamp=datetime.now(),
            details=details
        )
        
        self.history.append(history_entry)

    async def generate_test_notification(self, user_id: str, test_type: str) -> Dict[str, Any]:
        """Generate test notification for development"""
        test_templates = {
            "success": {
                "title": "Operation Successful",
                "message": "Your test operation completed successfully",
                "type": "success",
                "priority": "medium"
            },
            "error": {
                "title": "System Error",
                "message": "A test error occurred in the system",
                "type": "error",
                "priority": "high"
            },
            "warning": {
                "title": "Warning Alert",
                "message": "This is a test warning notification",
                "type": "warning",
                "priority": "medium"
            },
            "info": {
                "title": "Information Update",
                "message": "Test information notification",
                "type": "info",
                "priority": "low"
            }
        }
        
        template = test_templates.get(test_type, test_templates["info"])
        template["userId"] = user_id
        template["data"] = {"test": True, "generated_at": datetime.now().isoformat()}
        
        notification = await self.create_notification(template)
        
        # Add history entry for sending test notification
        await self.add_history_entry(
            notification.id, "sent", {"channel": "test", "test_type": test_type, "timestamp": datetime.now().isoformat()}
        )
        
        return {
            "id": notification.id,
            "title": notification.title,
            "message": notification.message,
            "type": notification.type.value,
            "priority": notification.priority.value,
            "timestamp": notification.timestamp.isoformat(),
            "userId": notification.userId,
            "data": notification.data
        }
