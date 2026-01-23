import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db
from app.models import Base

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


def test_health_check():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_provision_resource():
    r = client.post(
        "/api/resources/provision",
        json={
            "name": "test-instance",
            "type": "compute",
            "provider": "aws",
            "region": "us-east-1",
            "team": "engineering",
            "size": 2,
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "test-instance"
    assert data["state"] == "validating"


def test_list_resources():
    r = client.get("/api/resources")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_cost_optimization_summary():
    r = client.get("/api/cost/summary")
    assert r.status_code == 200
    data = r.json()
    assert "total_recommendations" in data
    assert "total_potential_savings" in data


def test_compliance_summary():
    r = client.get("/api/compliance/summary")
    assert r.status_code == 200
    assert "compliance_rate" in r.json()


def test_dashboard_stats():
    r = client.get("/api/stats/dashboard")
    assert r.status_code == 200
    data = r.json()
    assert "resources" in data
    assert "costs" in data
    assert "compliance" in data
