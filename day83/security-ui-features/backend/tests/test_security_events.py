import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_security_events():
    response = client.get("/api/security/events/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_event_summary():
    response = client.get("/api/security/events/stats/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_events" in data
    assert "unresolved_events" in data
    assert "severity_breakdown" in data

def test_get_dashboard_metrics():
    response = client.get("/api/security/metrics/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "active_threats" in data
    assert "events_last_hour" in data
    assert "avg_threat_score" in data

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
