import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.utils.database import get_db
from app.models.task import Base as TaskBase
from app.models.worker import Base as WorkerBase

# Test database
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_database():
    TaskBase.metadata.create_all(bind=engine)
    WorkerBase.metadata.create_all(bind=engine)
    yield
    TaskBase.metadata.drop_all(bind=engine)
    WorkerBase.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_create_task():
    response = client.post(
        "/api/tasks/",
        json={
            "name": "Test Task",
            "payload": {"test": True},
            "queue_name": "test",
            "priority": 1
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Task"
    assert data["status"] == "queued"

def test_get_metrics():
    response = client.get("/api/monitoring/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "tasks" in data
    assert "workers" in data
    assert "system" in data

def test_register_worker():
    response = client.post(
        "/api/workers/register",
        params={
            "worker_id": "test-worker",
            "name": "Test Worker",
            "host": "localhost",
            "port": 8001
        }
    )
    assert response.status_code == 200

def test_worker_heartbeat():
    # First register worker
    client.post(
        "/api/workers/register",
        params={
            "worker_id": "test-worker",
            "name": "Test Worker", 
            "host": "localhost",
            "port": 8001
        }
    )
    
    # Send heartbeat
    response = client.post(
        "/api/workers/test-worker/heartbeat",
        json={
            "worker_id": "test-worker",
            "cpu_usage": 50.0,
            "memory_usage": 60.0,
            "task_count": 2,
            "is_healthy": True
        }
    )
    assert response.status_code == 200

def test_task_processing():
    # Create task
    response = client.post(
        "/api/tasks/",
        json={
            "name": "Process Test Task",
            "payload": {"test": True}
        }
    )
    task_id = response.json()["id"]
    
    # Process task
    response = client.post(
        f"/api/tasks/{task_id}/process",
        params={"worker_id": "test-worker"}
    )
    assert response.status_code == 200

def test_health_check():
    response = client.get("/api/monitoring/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
