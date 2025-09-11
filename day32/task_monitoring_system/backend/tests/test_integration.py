import pytest
import asyncio
import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_complete_workflow():
    """Test complete task lifecycle"""
    
    # 1. Register a worker
    worker_response = client.post(
        "/api/workers/register",
        params={
            "worker_id": "integration-worker",
            "name": "Integration Test Worker",
            "host": "localhost",
            "port": 9000
        }
    )
    assert worker_response.status_code == 200
    
    # 2. Create a task
    task_response = client.post(
        "/api/tasks/",
        json={
            "name": "Integration Test Task",
            "payload": {"integration": True},
            "priority": 5
        }
    )
    assert task_response.status_code == 200
    task_data = task_response.json()
    task_id = task_data["id"]
    assert task_data["status"] == "queued"
    
    # 3. Send worker heartbeat
    heartbeat_response = client.post(
        f"/api/workers/integration-worker/heartbeat",
        json={
            "worker_id": "integration-worker",
            "cpu_usage": 25.0,
            "memory_usage": 40.0,
            "task_count": 1,
            "is_healthy": True
        }
    )
    assert heartbeat_response.status_code == 200
    
    # 4. Process the task
    process_response = client.post(
        f"/api/tasks/{task_id}/process",
        params={"worker_id": "integration-worker"}
    )
    assert process_response.status_code == 200
    
    # 5. Check task status (should be processing)
    status_response = client.get(f"/api/tasks/{task_id}")
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert status_data["status"] == "processing"
    assert status_data["worker_id"] == "integration-worker"
    
    # 6. Wait for task completion (simulated)
    time.sleep(3)
    
    # 7. Check final status (should be completed or failed)
    final_response = client.get(f"/api/tasks/{task_id}")
    final_data = final_response.json()
    assert final_data["status"] in ["completed", "failed"]
    
    # 8. Check metrics
    metrics_response = client.get("/api/monitoring/metrics")
    assert metrics_response.status_code == 200
    metrics_data = metrics_response.json()
    assert "tasks" in metrics_data
    assert "workers" in metrics_data
    
    # 9. Check worker health
    health_response = client.get("/api/monitoring/workers/health")
    assert health_response.status_code == 200
    health_data = health_response.json()
    assert health_data["total_workers"] >= 1

def test_error_handling():
    """Test error scenarios"""
    
    # Try to get non-existent task
    response = client.get("/api/tasks/999999")
    assert response.status_code == 404
    
    # Try to process non-existent task
    response = client.post("/api/tasks/999999/process", params={"worker_id": "test"})
    assert response.status_code == 404
    
    # Try to send heartbeat for non-existent worker
    response = client.post(
        "/api/workers/nonexistent/heartbeat",
        json={
            "worker_id": "nonexistent",
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "task_count": 0,
            "is_healthy": True
        }
    )
    assert response.status_code == 404
