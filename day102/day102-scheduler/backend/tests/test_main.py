import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import engine
from app.models import Base

@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)

def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Scheduling" in r.json()["message"]

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200

def test_dashboard(client):
    r = client.get("/api/dashboard")
    assert r.status_code == 200
    d = r.json()
    assert "jobs" in d
    assert "executions" in d

def test_create_job_and_trigger(client):
    r = client.post("/api/jobs", json={"name": "test-job", "command": "echo hello"})
    assert r.status_code == 200
    job_id = r.json()["id"]
    r2 = client.post(f"/api/jobs/{job_id}/trigger")
    assert r2.status_code == 200
    r3 = client.get("/api/dashboard")
    assert r3.json()["executions"] > 0
