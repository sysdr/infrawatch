import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_export_job():
    response = client.post("/api/exports", json={
        "export_type": "metrics",
        "format": "csv",
        "filters": {}
    })
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["status"] == "pending"

def test_list_export_jobs():
    response = client.get("/api/exports")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_stats():
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_jobs" in data
    assert "active_schedules" in data

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
