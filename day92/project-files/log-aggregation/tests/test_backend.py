import pytest
import asyncio
from httpx import AsyncClient
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))

from main import app

@pytest.mark.asyncio
async def test_ingest_log():
    """Test log ingestion"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/logs/ingest", json={
            "timestamp": datetime.utcnow().isoformat(),
            "level": "INFO",
            "service": "test-service",
            "message": "Test log message",
            "structured_data": '{"key": "value"}'
        })
        assert response.status_code == 200
        assert response.json()["success"] == True

@pytest.mark.asyncio
async def test_batch_ingest():
    """Test batch log ingestion"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        logs = [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "level": "INFO",
                "service": "test-service",
                "message": f"Test log {i}"
            }
            for i in range(10)
        ]
        response = await client.post("/api/logs/ingest/batch", json=logs)
        assert response.status_code == 200
        assert response.json()["count"] == 10

@pytest.mark.asyncio
async def test_get_logs():
    """Test log retrieval"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/logs?limit=10")
        assert response.status_code == 200
        assert "logs" in response.json()

@pytest.mark.asyncio
async def test_get_parsers():
    """Test parser retrieval"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/parsers")
        assert response.status_code == 200
        assert "parsers" in response.json()

@pytest.mark.asyncio
async def test_metrics():
    """Test metrics endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/metrics/summary")
        assert response.status_code == 200
        data = response.json()
        assert "total_logs" in data
        assert "storage" in data
