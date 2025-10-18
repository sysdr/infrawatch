from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from models.notification import Notification
import logging

logger = logging.getLogger(__name__)

class NotificationChannel(ABC):
    """Base class for all notification channels"""
    
    def __init__(self):
        self.name = self.__class__.__name__
    
    @abstractmethod
    async def send(self, notification: Notification) -> Dict[str, Any]:
        """Send notification through this channel"""
        pass
    
    @abstractmethod
    def validate_recipient(self, recipient: str) -> bool:
        """Validate recipient format for this channel"""
        pass
    
    async def format_message(self, notification: Notification) -> Dict[str, str]:
        """Format message for this channel"""
        return {
            "title": notification.title,
            "body": notification.message
        }
    
    def get_retry_delay(self, attempt: int) -> int:
        """Get exponential backoff delay for retries"""
        return min(300, (2 ** attempt) * 5)  # Max 5 minutes
