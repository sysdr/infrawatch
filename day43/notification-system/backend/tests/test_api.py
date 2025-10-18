import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestNotificationAPI:
    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "Notification System API" in response.json()["message"]

    def test_create_notification_success(self):
        notification_data = {
            "title": "Test API Notification",
            "message": "This is a test notification via API",
            "channel": "email",
            "recipient": "test@example.com",
            "priority": "medium"
        }
        
        response = client.post("/notifications", json=notification_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == notification_data["title"]
        assert data["channel"] == notification_data["channel"]
        assert data["status"] == "pending"

    def test_create_notification_invalid_data(self):
        invalid_data = {
            "title": "",  # Empty title
            "message": "Test message",
            "channel": "email",
            "recipient": "invalid-email",  # Invalid email
            "priority": "medium"
        }
        
        response = client.post("/notifications", json=invalid_data)
        assert response.status_code == 400
        assert "errors" in response.json()["detail"]

    def test_get_notifications(self):
        response = client.get("/notifications")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_notifications_with_pagination(self):
        response = client.get("/notifications?skip=0&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5

    def test_test_channel_email(self):
        test_data = {
            "channel": "email",
            "recipient": "test@example.com",
            "test_message": "API test message"
        }
        
        response = client.post("/channels/test", json=test_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["channel"] == "email"
        assert data["recipient"] == "test@example.com"
        assert "result" in data

    def test_test_channel_invalid_recipient(self):
        test_data = {
            "channel": "email",
            "recipient": "invalid-email",
            "test_message": "API test message"
        }
        
        response = client.post("/channels/test", json=test_data)
        assert response.status_code == 400

    def test_get_channel_status(self):
        response = client.get("/channels/status")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        # Should contain all channel types
        expected_channels = ["email", "sms", "slack", "webhook", "push"]
        for channel in expected_channels:
            assert channel in data

    def test_get_stats(self):
        response = client.get("/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_notifications" in data
        assert "total_delivered" in data
        assert "total_failed" in data
        assert "channels" in data
        assert "uptime" in data

    def test_create_bulk_notifications(self):
        bulk_data = {
            "notifications": [
                {
                    "title": "Bulk Test 1",
                    "message": "First bulk notification",
                    "channel": "email",
                    "recipient": "test1@example.com",
                    "priority": "medium"
                },
                {
                    "title": "Bulk Test 2", 
                    "message": "Second bulk notification",
                    "channel": "sms",
                    "recipient": "+1234567890",
                    "priority": "high"
                }
            ]
        }
        
        response = client.post("/notifications/bulk", json=bulk_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "notification_ids" in data
        assert len(data["notification_ids"]) == 2

    def test_get_notification_by_id_not_found(self):
        response = client.get("/notifications/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

class TestChannelSpecificTests:
    def test_sms_channel(self):
        test_data = {
            "channel": "sms",
            "recipient": "+1234567890",
            "test_message": "SMS test"
        }
        
        response = client.post("/channels/test", json=test_data)
        assert response.status_code == 200

    def test_slack_channel(self):
        test_data = {
            "channel": "slack",
            "recipient": "#general",
            "test_message": "Slack test"
        }
        
        response = client.post("/channels/test", json=test_data)
        assert response.status_code == 200

    def test_webhook_channel(self):
        test_data = {
            "channel": "webhook",
            "recipient": "https://api.example.com/webhook",
            "test_message": "Webhook test"
        }
        
        response = client.post("/channels/test", json=test_data)
        assert response.status_code == 200

    def test_push_channel(self):
        test_data = {
            "channel": "push",
            "recipient": "demo_device_token_12345",
            "test_message": "Push test"
        }
        
        response = client.post("/channels/test", json=test_data)
        assert response.status_code == 200
