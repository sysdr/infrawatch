import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
from app.services.data_generator import seed_database

TEST_DB = "sqlite:///./test_analytics.db"
engine  = create_engine(TEST_DB, connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def override_db():
    db = TestSession()
    try:
        seed_database(db)
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_db
client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"

def test_pipeline_status():
    r = client.get("/api/analytics/pipeline")
    assert r.status_code == 200
    data = r.json()
    assert "status" in data

def test_ingest_event():
    payload = {
        "event_type": "page_view",
        "user_id": "test_user_1",
        "session_id": "sess_abc",
        "page": "/home",
        "duration_ms": 1200.0,
        "revenue": 0.0,
        "properties": {"source": "organic"}
    }
    r = client.post("/api/analytics/events", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["event_type"] == "page_view"
    assert data["status"] == "ingested"

def test_event_summary():
    r = client.get("/api/analytics/summary")
    assert r.status_code == 200
    data = r.json()
    assert "total_events" in data
    assert "by_type" in data

def test_kpis():
    r = client.get("/api/reports/kpis")
    assert r.status_code == 200
    data = r.json()
    assert "page_views" in data
    assert "revenue" in data
    assert "change_pct" in data["page_views"]

def test_report_summary():
    r = client.get("/api/reports/summary?days=7")
    assert r.status_code == 200
    data = r.json()
    assert "summary" in data
    assert "hourly" in data
    assert data["days"] == 7
