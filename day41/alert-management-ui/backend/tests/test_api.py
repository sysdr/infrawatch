import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_get_alerts():
    response = client.get("/api/alerts")
    assert response.status_code == 200
    assert "alerts" in response.json()

def test_get_alert_stats():
    response = client.get("/api/alerts/stats/summary")
    assert response.status_code == 200
    stats = response.json()
    assert "total" in stats
    assert "critical" in stats

def test_acknowledge_alert():
    response = client.post("/api/alerts/alert_1/acknowledge")
    assert response.status_code == 200

def test_bulk_acknowledge():
    response = client.post("/api/alerts/bulk/acknowledge", 
                          json={"alert_ids": ["alert_1", "alert_2"]})
    assert response.status_code == 200
