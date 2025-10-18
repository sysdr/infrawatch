from channels.base import NotificationChannel
from models.notification import Notification
from config.settings import settings
import logging
from typing import Dict, Any
import json

logger = logging.getLogger(__name__)

class SlackChannel(NotificationChannel):
    """Slack notification channel"""
    
    def __init__(self):
        super().__init__()
        self.bot_token = settings.slack_bot_token
        self.webhook_url = settings.slack_webhook_url
    
    def validate_recipient(self, recipient: str) -> bool:
        """Validate Slack channel or user format"""
        # Channel: #channel-name or User: @username or User ID: U1234567890
        return (recipient.startswith('#') or 
                recipient.startswith('@') or 
                recipient.startswith('U') or
                recipient.startswith('C'))
    
    async def send(self, notification: Notification) -> Dict[str, Any]:
        """Send Slack notification"""
        try:
            if not self.validate_recipient(notification.recipient):
                raise ValueError(f"Invalid Slack recipient: {notification.recipient}")
            
            formatted_msg = await self.format_message(notification)
            
            # Demo implementation - simulate Slack API
            logger.info(f"💬 Sending Slack message to {notification.recipient}")
            logger.info(f"Message: {formatted_msg['body']}")
            
            # Simulate API response
            return {
                "success": True,
                "message_id": f"slack_{notification.id}_demo",
                "provider": "slack",
                "cost": 0.0  # Slack is free for most use cases
            }
            
        except Exception as e:
            logger.error(f"Slack send failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "provider": "slack"
            }
    
    async def format_message(self, notification: Notification) -> Dict[str, str]:
        """Format Slack message with blocks"""
        
        priority_colors = {
            "low": "#36a64f",      # Green
            "medium": "#ff9500",   # Orange  
            "high": "#ff0000",     # Red
            "critical": "#8B0000"   # Dark Red
        }
        
        color = priority_colors.get(notification.priority.value, "#36a64f")
        
        # Slack block format
        blocks = {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{notification.title}*\n{notification.message}"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"Priority: *{notification.priority.value.upper()}* | Created: {notification.created_at}"
                        }
                    ]
                }
            ],
            "attachments": [
                {
                    "color": color,
                    "blocks": [
                        {
                            "type": "actions",
                            "elements": [
                                {
                                    "type": "button",
                                    "text": {"type": "plain_text", "text": "Acknowledge"},
                                    "style": "primary",
                                    "value": f"ack_{notification.id}"
                                },
                                {
                                    "type": "button", 
                                    "text": {"type": "plain_text", "text": "View Details"},
                                    "value": f"details_{notification.id}"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        return {
            "title": notification.title,
            "body": json.dumps(blocks),
            "color": color
        }
