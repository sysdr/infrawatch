import pytest
import asyncio
from app.services.delivery_service import DeliveryService, DeliveryStatus
from app.services.websocket_manager import WebSocketManager

@pytest.mark.asyncio
async def test_email_delivery():
    """Test email delivery simulation"""
    websocket_manager = WebSocketManager()
    delivery_service = DeliveryService(websocket_manager)
    
    notification_data = {
        "id": "test_001",
        "channel": "email",
        "recipient": "test@example.com",
        "content": "Test email content",
        "priority": "normal"
    }
    
    result = await delivery_service.deliver_notification(notification_data)
    
    assert result.status in [DeliveryStatus.SUCCESS, DeliveryStatus.FAILED_TEMPORARY]
    assert result.delivery_time_ms > 0
    assert result.message is not None

@pytest.mark.asyncio
async def test_sms_delivery():
    """Test SMS delivery simulation"""
    websocket_manager = WebSocketManager()
    delivery_service = DeliveryService(websocket_manager)
    
    notification_data = {
        "id": "test_002",
        "channel": "sms",
        "recipient": "+1234567890",
        "content": "Test SMS content",
        "priority": "normal"
    }
    
    result = await delivery_service.deliver_notification(notification_data)
    
    assert result.status in [DeliveryStatus.SUCCESS, DeliveryStatus.FAILED_TEMPORARY, DeliveryStatus.RATE_LIMITED]
    assert result.delivery_time_ms > 0

@pytest.mark.asyncio
async def test_push_delivery():
    """Test push notification delivery simulation"""
    websocket_manager = WebSocketManager()
    delivery_service = DeliveryService(websocket_manager)
    
    notification_data = {
        "id": "test_003",
        "channel": "push",
        "recipient": "device_token_123",
        "content": "Test push content",
        "priority": "urgent"
    }
    
    result = await delivery_service.deliver_notification(notification_data)
    
    assert result.status in [DeliveryStatus.SUCCESS, DeliveryStatus.FAILED_TEMPORARY, DeliveryStatus.FAILED_PERMANENT]
    assert result.delivery_time_ms > 0

def test_delivery_stats():
    """Test delivery statistics tracking"""
    websocket_manager = WebSocketManager()
    delivery_service = DeliveryService(websocket_manager)
    
    initial_stats = delivery_service.get_stats()
    assert initial_stats["total_sent"] == 0
    assert initial_stats["successful"] == 0
