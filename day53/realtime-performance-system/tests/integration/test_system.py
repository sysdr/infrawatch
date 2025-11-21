import pytest
import asyncio
import json
from httpx import AsyncClient
import websockets

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"

@pytest.mark.asyncio
async def test_notification_creation():
    """Test creating a notification"""
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.post("/api/notifications/", json={
            "user_id": "test_user",
            "message": "Test notification",
            "priority": "normal",
            "notification_type": "info"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "test_user"
        assert data["message"] == "Test notification"

@pytest.mark.asyncio
async def test_bulk_notifications():
    """Test creating bulk notifications"""
    notifications = [
        {
            "user_id": f"user_{i}",
            "message": f"Bulk message {i}",
            "priority": "normal",
            "notification_type": "info"
        }
        for i in range(100)
    ]
    
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.post("/api/notifications/bulk", json=notifications)
        assert response.status_code == 200
        data = response.json()
        assert data["created"] == 100

@pytest.mark.asyncio
async def test_metrics_endpoint():
    """Test metrics retrieval"""
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.get("/api/metrics/current")
        assert response.status_code == 200
        data = response.json()
        assert "active_connections" in data
        assert "memory_usage_mb" in data

@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health check"""
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
