import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Notification Delivery System"
    assert data["status"] == "running"

def test_send_notification():
    """Test sending notification"""
    notification_data = {
        "user_id": 1,
        "channel": "email",
        "priority": "normal",
        "recipient": "test@example.com",
        "subject": "Test Subject",
        "content": "Test notification content"
    }
    
    response = client.post("/api/notifications/send", json=notification_data)
    assert response.status_code == 200
    data = response.json()
    assert "notification_id" in data
    assert "tracking_id" in data
    assert data["status"] == "queued"

def test_get_delivery_stats():
    """Test delivery statistics endpoint"""
    response = client.get("/api/delivery/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_sent" in data
    assert "success_rate" in data
    assert "avg_delivery_time" in data

def test_tracking_endpoint():
    """Test tracking endpoint"""
    tracking_id = "track_0001"
    response = client.get(f"/api/tracking/{tracking_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["tracking_id"] == tracking_id
    assert "current_status" in data
    assert "events" in data

def test_dashboard_metrics():
    """Test dashboard metrics endpoint"""
    response = client.get("/api/metrics/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "overview" in data
    assert "hourly_stats" in data
    assert "channel_breakdown" in data
