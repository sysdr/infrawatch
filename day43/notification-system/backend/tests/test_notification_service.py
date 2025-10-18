import pytest
import asyncio
from app.services.notification_service import NotificationService
from models.notification import Notification, NotificationChannel, NotificationPriority, NotificationStatus
from datetime import datetime

class TestNotificationService:
    def setup_method(self):
        self.service = NotificationService()
        self.test_notification = Notification(
            id=1,
            title="Test Notification",
            message="This is a test notification",
            channel=NotificationChannel.EMAIL,
            recipient="test@example.com",
            priority=NotificationPriority.MEDIUM,
            status=NotificationStatus.PENDING,
            created_at=datetime.utcnow()
        )

    @pytest.mark.asyncio
    async def test_send_notification_success(self):
        result = await self.service.send_notification(self.test_notification)
        assert result["success"] == True
        assert self.test_notification.status == NotificationStatus.DELIVERED
        assert self.test_notification.delivered_at is not None

    def test_validate_notification_valid(self):
        errors = self.service.validate_notification(self.test_notification)
        assert len(errors) == 0

    def test_validate_notification_invalid_recipient(self):
        invalid_notification = Notification(
            id=2,
            title="Invalid Test",
            message="Test message",
            channel=NotificationChannel.EMAIL,
            recipient="invalid-email",
            priority=NotificationPriority.MEDIUM,
            status=NotificationStatus.PENDING,
            created_at=datetime.utcnow()
        )
        
        errors = self.service.validate_notification(invalid_notification)
        assert len(errors) > 0
        assert any("Invalid recipient format" in error for error in errors)

    def test_validate_notification_missing_title(self):
        invalid_notification = Notification(
            id=3,
            title="",
            message="Test message",
            channel=NotificationChannel.EMAIL,
            recipient="test@example.com",
            priority=NotificationPriority.MEDIUM,
            status=NotificationStatus.PENDING,
            created_at=datetime.utcnow()
        )
        
        errors = self.service.validate_notification(invalid_notification)
        assert len(errors) > 0
        assert any("Title is required" in error for error in errors)

    @pytest.mark.asyncio
    async def test_send_bulk_notifications(self):
        notifications = [
            Notification(
                id=i,
                title=f"Test Notification {i}",
                message=f"This is test notification {i}",
                channel=NotificationChannel.EMAIL,
                recipient="test@example.com",
                priority=NotificationPriority.MEDIUM,
                status=NotificationStatus.PENDING,
                created_at=datetime.utcnow()
            ) for i in range(1, 4)
        ]
        
        results = await self.service.send_bulk_notifications(notifications)
        assert len(results) == 3
        assert all(result.get("success") for result in results)

    @pytest.mark.asyncio
    async def test_get_channel_stats(self):
        stats = await self.service.get_channel_stats()
        assert isinstance(stats, dict)
        assert "email" in stats
        assert "sms" in stats
        assert "slack" in stats
        assert "webhook" in stats
        assert "push" in stats
        
        for channel_stats in stats.values():
            assert "name" in channel_stats
            assert "available" in channel_stats
            assert "last_check" in channel_stats
