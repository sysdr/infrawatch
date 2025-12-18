import pytest
from httpx import AsyncClient
from app.main import app
from datetime import datetime, timedelta

@pytest.mark.asyncio
async def test_get_metrics():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/dashboard/metrics")
        assert response.status_code == 200
        data = response.json()
        assert 'metrics' in data
        assert 'count' in data

@pytest.mark.asyncio
async def test_get_aggregated():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/dashboard/aggregated",
            params={'group_by': 'service', 'metric_name': 'latency'}
        )
        assert response.status_code == 200
        data = response.json()
        assert 'data' in data

@pytest.mark.asyncio
async def test_filters_available():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/filters/available")
        assert response.status_code == 200
        data = response.json()
        assert 'services' in data
        assert 'regions' in data

print("✅ All tests passed")
