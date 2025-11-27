import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.database import SessionLocal, engine, Base
from app.models.notification import Notification, NotificationType
from datetime import datetime

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Create test notifications
    for i in range(100):
        notification = Notification(
            user_id=1,
            title=f"Test Notification {i}",
            message=f"Test message {i}",
            notification_type=NotificationType.INFO,
            is_read=0
        )
        db.add(notification)
    db.commit()
    db.close()
    
    yield
    
    Base.metadata.drop_all(bind=engine)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_csv_export(setup_database):
    response = client.post("/api/exports/create", json={
        "export_format": "csv",
        "user_id": 1
    })
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "pending"

def test_create_json_export(setup_database):
    response = client.post("/api/exports/create", json={
        "export_format": "json"
    })
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data

def test_get_export_status(setup_database):
    # Create export first
    create_response = client.post("/api/exports/create", json={
        "export_format": "csv"
    })
    job_id = create_response.json()["job_id"]
    
    # Get status
    response = client.get(f"/api/exports/{job_id}/status")
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == job_id
    assert "status" in data

def test_list_exports(setup_database):
    response = client.get("/api/exports/list")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
