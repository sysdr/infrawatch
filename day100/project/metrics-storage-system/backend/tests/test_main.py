import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert "Metrics Storage" in r.json()["message"]

def test_store_metrics():
    r = client.post("/metrics/store", json=[{
        "measurement": "cpu_usage",
        "source": "test",
        "type": "system",
        "value": 75.5,
        "timestamp": "2025-02-04T12:00:00"
    }])
    assert r.status_code == 200
    assert r.json()["count"] == 1

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"

def test_api_metrics_returns_nonzero_after_store():
    """Verify /api/metrics returns non-zero for dashboard validation"""
    client.post("/metrics/store", json=[
        {"measurement": "cpu_usage", "source": "test", "type": "system", "value": 65.0, "timestamp": "2025-02-04T12:00:00"},
        {"measurement": "memory_usage", "source": "test", "type": "system", "value": 70.0, "timestamp": "2025-02-04T12:00:00"},
        {"measurement": "disk_usage", "source": "test", "type": "system", "value": 40.0, "timestamp": "2025-02-04T12:00:00"},
    ])
    r = client.get("/api/metrics")
    assert r.status_code == 200
    data = r.json()
    assert "summary" in data
    s = data["summary"]
    assert s["total"] > 0
    assert s.get("cpu_avg", 0) > 0 or s.get("memory_avg", 0) > 0 or s.get("disk_avg", 0) > 0
