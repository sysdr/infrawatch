import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app, get_db
from app.models import Base
from app.models import Task, TaskStatus, TaskPriority

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_create_task():
    response = client.post(
        "/api/tasks",
        json={
            "task_type": "collect_system_metrics",
            "priority": 5,  # TaskPriority.NORMAL value
            "payload": {"test": "data"}
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["task_type"] == "collect_system_metrics"
    assert data["status"] == "pending"

def test_get_tasks():
    response = client.get("/api/tasks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
