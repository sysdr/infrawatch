from models.notification import Notification, NotificationStatus, NotificationChannel
from channels.email import EmailChannel
from channels.sms import SMSChannel
from channels.slack import SlackChannel
from channels.webhook import WebhookChannel
from channels.push import PushChannel
from typing import Dict, List, Any
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class NotificationService:
    """Core notification service that routes and sends notifications"""
    
    def __init__(self):
        self.channels = {
            NotificationChannel.EMAIL: EmailChannel(),
            NotificationChannel.SMS: SMSChannel(),
            NotificationChannel.SLACK: SlackChannel(),
            NotificationChannel.WEBHOOK: WebhookChannel(),
            NotificationChannel.PUSH: PushChannel()
        }
    
    async def send_notification(self, notification: Notification) -> Dict[str, Any]:
        """Send a single notification"""
        try:
            # Update status
            notification.status = NotificationStatus.PROCESSING
            
            # Get appropriate channel
            channel = self.channels.get(notification.channel)
            if not channel:
                raise ValueError(f"Unsupported channel: {notification.channel}")
            
            # Send notification
            result = await channel.send(notification)
            
            # Update status based on result
            if result.get("success"):
                notification.status = NotificationStatus.DELIVERED
                notification.delivered_at = datetime.utcnow()
                logger.info(f"✅ Notification {notification.id} delivered via {notification.channel.value}")
            else:
                notification.status = NotificationStatus.FAILED
                notification.error_message = result.get("error", "Unknown error")
                logger.error(f"❌ Notification {notification.id} failed: {notification.error_message}")
            
            return result
            
        except Exception as e:
            notification.status = NotificationStatus.FAILED
            notification.error_message = str(e)
            logger.error(f"❌ Notification {notification.id} exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def send_bulk_notifications(self, notifications: List[Notification]) -> List[Dict[str, Any]]:
        """Send multiple notifications concurrently"""
        tasks = [self.send_notification(notif) for notif in notifications]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        formatted_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                formatted_results.append({
                    "success": False,
                    "error": str(result),
                    "notification_id": notifications[i].id
                })
            else:
                formatted_results.append(result)
        
        return formatted_results
    
    def validate_notification(self, notification: Notification) -> List[str]:
        """Validate notification before sending"""
        errors = []
        
        # Check if channel is supported
        if notification.channel not in self.channels:
            errors.append(f"Unsupported channel: {notification.channel}")
            return errors
        
        # Validate recipient format
        channel = self.channels[notification.channel]
        if not channel.validate_recipient(notification.recipient):
            errors.append(f"Invalid recipient format for {notification.channel.value}: {notification.recipient}")
        
        # Check required fields
        if not notification.title or not notification.title.strip():
            errors.append("Title is required")
        
        if not notification.message or not notification.message.strip():
            errors.append("Message is required")
        
        return errors
    
    async def get_channel_stats(self) -> Dict[str, Any]:
        """Get statistics for all channels"""
        stats = {}
        for channel_type, channel in self.channels.items():
            stats[channel_type.value] = {
                "name": channel.name,
                "available": True,  # In production, check channel health
                "last_check": datetime.utcnow().isoformat()
            }
        return stats
