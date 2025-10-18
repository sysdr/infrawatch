import pytest
import asyncio
from models.notification import Notification, NotificationChannel, NotificationPriority, NotificationStatus
from channels.email import EmailChannel
from channels.sms import SMSChannel
from channels.slack import SlackChannel
from channels.webhook import WebhookChannel
from channels.push import PushChannel
from datetime import datetime

class TestEmailChannel:
    def setup_method(self):
        self.channel = EmailChannel()
        self.notification = Notification(
            id=1,
            title="Test Email",
            message="This is a test email message",
            channel=NotificationChannel.EMAIL,
            recipient="test@example.com",
            priority=NotificationPriority.MEDIUM,
            status=NotificationStatus.PENDING,
            created_at=datetime.utcnow()
        )

    def test_validate_recipient_valid_email(self):
        assert self.channel.validate_recipient("test@example.com") == True
        assert self.channel.validate_recipient("user.name+tag@domain.co.uk") == True

    def test_validate_recipient_invalid_email(self):
        assert self.channel.validate_recipient("invalid-email") == False
        assert self.channel.validate_recipient("@domain.com") == False
        assert self.channel.validate_recipient("user@") == False

    @pytest.mark.asyncio
    async def test_send_success(self):
        result = await self.channel.send(self.notification)
        assert result["success"] == True
        assert "message_id" in result
        assert result["provider"] == "sendgrid"

    @pytest.mark.asyncio
    async def test_format_message(self):
        formatted = await self.channel.format_message(self.notification)
        assert "title" in formatted
        assert "body" in formatted
        assert "html_body" in formatted
        assert "[MEDIUM]" in formatted["title"]

class TestSMSChannel:
    def setup_method(self):
        self.channel = SMSChannel()
        self.notification = Notification(
            id=2,
            title="Test SMS",
            message="This is a test SMS message",
            channel=NotificationChannel.SMS,
            recipient="+1234567890",
            priority=NotificationPriority.HIGH,
            status=NotificationStatus.PENDING,
            created_at=datetime.utcnow()
        )

    def test_validate_recipient_valid_phone(self):
        assert self.channel.validate_recipient("+1234567890") == True
        assert self.channel.validate_recipient("+44123456789") == True

    def test_validate_recipient_invalid_phone(self):
        assert self.channel.validate_recipient("invalid-phone") == False
        assert self.channel.validate_recipient("123") == False

    @pytest.mark.asyncio
    async def test_send_success(self):
        result = await self.channel.send(self.notification)
        assert result["success"] == True
        assert result["provider"] == "twilio"

    @pytest.mark.asyncio
    async def test_format_message_truncation(self):
        # Create long message
        long_notification = Notification(
            id=3,
            title="Very Long Title That Should Be Truncated",
            message="This is a very long message that exceeds the 160 character limit for SMS messages and should be truncated with ellipsis",
            channel=NotificationChannel.SMS,
            recipient="+1234567890",
            priority=NotificationPriority.CRITICAL,
            status=NotificationStatus.PENDING,
            created_at=datetime.utcnow()
        )
        
        formatted = await self.channel.format_message(long_notification)
        assert len(formatted["body"]) <= 160
        assert formatted["body"].endswith("...")

class TestSlackChannel:
    def setup_method(self):
        self.channel = SlackChannel()
        self.notification = Notification(
            id=4,
            title="Test Slack",
            message="This is a test Slack message",
            channel=NotificationChannel.SLACK,
            recipient="#general",
            priority=NotificationPriority.LOW,
            status=NotificationStatus.PENDING,
            created_at=datetime.utcnow()
        )

    def test_validate_recipient_valid_slack(self):
        assert self.channel.validate_recipient("#general") == True
        assert self.channel.validate_recipient("@username") == True
        assert self.channel.validate_recipient("U1234567890") == True
        assert self.channel.validate_recipient("C1234567890") == True

    def test_validate_recipient_invalid_slack(self):
        assert self.channel.validate_recipient("invalid") == False
        assert self.channel.validate_recipient("") == False

    @pytest.mark.asyncio
    async def test_send_success(self):
        result = await self.channel.send(self.notification)
        assert result["success"] == True
        assert result["provider"] == "slack"

    @pytest.mark.asyncio
    async def test_format_message_blocks(self):
        formatted = await self.channel.format_message(self.notification)
        assert "body" in formatted
        # Should contain Slack blocks JSON
        import json
        blocks = json.loads(formatted["body"])
        assert "blocks" in blocks
        assert "attachments" in blocks

class TestWebhookChannel:
    def setup_method(self):
        self.channel = WebhookChannel()
        self.notification = Notification(
            id=5,
            title="Test Webhook",
            message="This is a test webhook notification",
            channel=NotificationChannel.WEBHOOK,
            recipient="https://api.example.com/webhook",
            priority=NotificationPriority.MEDIUM,
            status=NotificationStatus.PENDING,
            created_at=datetime.utcnow()
        )

    def test_validate_recipient_valid_url(self):
        assert self.channel.validate_recipient("https://api.example.com/webhook") == True
        assert self.channel.validate_recipient("http://localhost:3000/hook") == True

    def test_validate_recipient_invalid_url(self):
        assert self.channel.validate_recipient("not-a-url") == False
        assert self.channel.validate_recipient("ftp://example.com") == False

    @pytest.mark.asyncio
    async def test_send_success(self):
        result = await self.channel.send(self.notification)
        assert result["success"] == True
        assert result["provider"] == "webhook"

class TestPushChannel:
    def setup_method(self):
        self.channel = PushChannel()
        self.notification = Notification(
            id=6,
            title="Test Push",
            message="This is a test push notification",
            channel=NotificationChannel.PUSH,
            recipient="demo_device_token_12345",
            priority=NotificationPriority.CRITICAL,
            status=NotificationStatus.PENDING,
            created_at=datetime.utcnow()
        )

    def test_validate_recipient_valid_token(self):
        assert self.channel.validate_recipient("demo_device_token_12345") == True

    def test_validate_recipient_invalid_token(self):
        assert self.channel.validate_recipient("short") == False
        assert self.channel.validate_recipient("") == False

    @pytest.mark.asyncio
    async def test_send_success(self):
        result = await self.channel.send(self.notification)
        assert result["success"] == True
        assert result["provider"] == "firebase"

    @pytest.mark.asyncio
    async def test_format_message_with_priority_icon(self):
        formatted = await self.channel.format_message(self.notification)
        assert "🔥" in formatted["title"]  # Critical priority icon
        assert "icon" in formatted
        assert "sound" in formatted
