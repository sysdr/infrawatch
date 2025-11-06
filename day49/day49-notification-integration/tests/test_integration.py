import pytest
import asyncio
import httpx
from datetime import datetime

BASE_URL = "http://localhost:8000"

@pytest.fixture
async def client():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        yield client

@pytest.mark.asyncio
async def test_health(client):
    """Test health endpoint"""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_create_preferences(client):
    """Test creating user preferences"""
    preferences = {
        "email": "test@example.com",
        "phone": "+1234567890",
        "slack_id": "U12345",
        "preferences": {
            "HIGH": {"channels": ["EMAIL", "SMS"]},
            "CRITICAL": {"channels": ["EMAIL", "SMS", "SLACK"]}
        }
    }
    
    response = await client.post("/api/preferences/test_user", json=preferences)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_create_alert_and_notifications(client):
    """Test creating alert triggers notifications"""
    # First create user preferences
    prefs = {
        "email": "alert_test@example.com",
        "phone": "+1987654321",
        "slack_id": "U67890",
        "preferences": {
            "CRITICAL": {"channels": ["EMAIL", "SMS", "SLACK"]}
        }
    }
    await client.post("/api/preferences/alert_user", json=prefs)
    
    # Create alert
    alert = {
        "service_name": "test-service",
        "alert_type": "CPU_HIGH",
        "severity": "CRITICAL",
        "message": "CPU usage exceeded 95%",
        "metadata": {"cpu_percent": 95.5}
    }
    
    response = await client.post("/api/alerts/", json=alert)
    assert response.status_code == 200
    alert_id = response.json()["id"]
    
    # Wait a bit for notifications to process
    await asyncio.sleep(2)
    
    # Check notifications were created
    response = await client.get(f"/api/notifications/?alert_id={alert_id}")
    assert response.status_code == 200
    notifications = response.json()
    assert len(notifications) > 0

@pytest.mark.asyncio
async def test_acknowledge_alert(client):
    """Test acknowledging an alert"""
    # Create alert
    alert = {
        "service_name": "test-service",
        "alert_type": "MEMORY_HIGH",
        "severity": "HIGH",
        "message": "Memory usage high",
        "metadata": {}
    }
    
    response = await client.post("/api/alerts/", json=alert)
    assert response.status_code == 200
    alert_id = response.json()["id"]
    
    # Acknowledge it
    response = await client.post(
        f"/api/alerts/{alert_id}/acknowledge",
        json={"user_id": "test_user"}
    )
    assert response.status_code == 200
    
    # Verify status changed
    response = await client.get("/api/alerts/")
    alerts = response.json()
    alert = next(a for a in alerts if a["id"] == alert_id)
    assert alert["status"] == "ACKNOWLEDGED"

@pytest.mark.asyncio
async def test_escalation_policy(client):
    """Test creating escalation policy"""
    policy = {
        "service_name": "critical-service",
        "severity": "CRITICAL",
        "policy_config": [
            {"level": 0, "users": ["oncall1", "oncall2"], "timeout_minutes": 5},
            {"level": 1, "users": ["manager1"], "timeout_minutes": 10}
        ]
    }
    
    response = await client.post("/api/escalations/", json=policy)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_notification_stats(client):
    """Test notification statistics endpoint"""
    response = await client.get("/api/notifications/stats")
    assert response.status_code == 200
    stats = response.json()
    assert "total" in stats
    assert "by_status" in stats
    assert "by_channel" in stats

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
