import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app

@pytest.mark.asyncio
async def test_chart_endpoint():
    """Test chart data endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/analytics/chart", params={
            "metric": "event_count",
            "group_by": "channel",
            "start": (datetime.utcnow() - timedelta(days=1)).isoformat(),
            "end": datetime.utcnow().isoformat()
        })
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "metadata" in data

@pytest.mark.asyncio
async def test_timeseries_endpoint():
    """Test time-series chart endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/analytics/chart/timeseries", params={
            "metric": "delivery_rate",
            "channels": "email,sms",
            "hours": 24
        })
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "channels" in data

@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health check"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
