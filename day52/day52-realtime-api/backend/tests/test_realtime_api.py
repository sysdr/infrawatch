import pytest
import asyncio
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models import Event, EventType

@pytest.fixture
def client():
    return TestClient(app)

@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

@pytest.mark.asyncio
async def test_metrics_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "connections" in data
        assert "events" in data

@pytest.mark.asyncio
async def test_create_event():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        event_data = {
            "type": "notification.created",
            "payload": {"message": "Test notification"}
        }
        response = await ac.post("/api/events", json=event_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "event_id" in data

def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "Real-time API Design"
