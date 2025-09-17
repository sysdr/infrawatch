import pytest
import asyncio
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_get_tasks():
    response = client.get("/api/tasks")
    assert response.status_code == 200
    data = response.json()
    assert "tasks" in data
    assert "total" in data

def test_get_queues():
    response = client.get("/api/queues")
    assert response.status_code == 200
    data = response.json()
    assert "queues" in data

def test_get_metrics():
    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "throughput" in data
    assert "latency" in data

def test_retry_task():
    response = client.post("/api/tasks/task-1/retry")
    assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__])
