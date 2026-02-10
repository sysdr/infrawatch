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
    assert "Integration" in r.json()["message"]

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200

def test_dashboard(client):
    r = client.get("/api/dashboard")
    assert r.status_code == 200
    d = r.json()
    assert "integrations" in d
    assert "webhooks_received" in d
    assert "events_processed" in d

def test_create_integration_and_webhook(client):
    r = client.post("/api/integrations", json={"name": "test-webhook", "type": "webhook"})
    assert r.status_code == 200
    iid = r.json()["id"]
    r2 = client.post(f"/api/webhook/{iid}", json={"source": "test", "payload": {}})
    assert r2.status_code == 200
    r3 = client.get("/api/dashboard")
    assert r3.json()["webhooks_received"] > 0
    assert r3.json()["events_processed"] > 0
