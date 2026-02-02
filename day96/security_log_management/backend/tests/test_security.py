import pytest
from fastapi.testclient import TestClient
from app.main import app
from datetime import datetime

client = TestClient(app)

def test_log_security_event():
    """Test security event logging"""
    event_data = {
        "event_type": "authentication",
        "severity": "medium",
        "user_id": "user123",
        "username": "testuser",
        "ip_address": "192.168.1.100",
        "resource": "/api/login",
        "action": "login",
        "result": "success",
        "details": {"method": "password"}
    }
    
    response = client.post("/api/security/events", json=event_data)
    assert response.status_code == 200
    data = response.json()
    assert "event_id" in data
    assert "event_hash" in data

def test_get_security_events():
    """Test retrieving security events"""
    response = client.get("/api/security/events?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "events" in data

def test_security_stats():
    """Test security statistics endpoint"""
    response = client.get("/api/security/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_events" in data
    assert "threats_detected" in data

def test_audit_trail():
    """Test audit trail retrieval"""
    response = client.get("/api/audit/trail?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "audit_trail" in data

def test_compliance_metrics():
    """Test compliance metrics"""
    response = client.get("/api/compliance/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "authentication" in data
    assert "incidents" in data
