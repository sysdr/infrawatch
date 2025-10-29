import pytest
import asyncio
from datetime import datetime
from app.services.queue_manager import QueueManager

@pytest.mark.asyncio
async def test_queue_manager_enqueue():
    """Test notification queuing"""
    queue_manager = QueueManager()
    
    notification_data = {
        "user_id": 1,
        "channel": "email",
        "priority": "high",
        "recipient": "test@example.com",
        "content": "Test notification"
    }
    
    notification_id = await queue_manager.enqueue_notification(notification_data)
    assert notification_id is not None
    assert notification_id.startswith("notif_")
    
    stats = queue_manager.get_stats()
    assert stats["queued"] == 1

@pytest.mark.asyncio
async def test_queue_manager_dequeue():
    """Test notification dequeuing"""
    queue_manager = QueueManager()
    
    # Add some notifications
    for i in range(5):
        await queue_manager.enqueue_notification({
            "user_id": i,
            "channel": "email",
            "priority": "normal",
            "recipient": f"user{i}@example.com",
            "content": f"Test notification {i}"
        })
    
    # Dequeue batch
    notifications = await queue_manager.dequeue_batch(batch_size=3)
    assert len(notifications) <= 3
    
    for notification in notifications:
        assert notification.notification_data["user_id"] >= 0
        assert notification.notification_data["channel"] == "email"

def test_priority_scoring():
    """Test priority score calculation"""
    queue_manager = QueueManager()
    
    assert queue_manager._get_priority_score("low") == 1
    assert queue_manager._get_priority_score("normal") == 5
    assert queue_manager._get_priority_score("high") == 8
    assert queue_manager._get_priority_score("urgent") == 10
    assert queue_manager._get_priority_score("invalid") == 5  # default
