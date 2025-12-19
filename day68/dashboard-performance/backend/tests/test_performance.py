import pytest
from httpx import AsyncClient
import time

from app.main import app

@pytest.mark.asyncio
async def test_dashboard_load_performance():
    """Test dashboard loads within acceptable time"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        start = time.time()
        response = await client.get("/api/dashboard/widgets?count=100")
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 1.0  # Should load in under 1 second
        assert len(response.json()["widgets"]) == 100

@pytest.mark.asyncio
async def test_cache_hit_rate():
    """Test cache provides significant hit rate"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First request (cache miss)
        response1 = await client.get("/api/dashboard/widgets?count=50")
        assert response1.json()["cached"] == False
        
        # Second request (cache hit)
        response2 = await client.get("/api/dashboard/widgets?count=50")
        assert response2.json()["cached"] == True

@pytest.mark.asyncio
async def test_downsampling():
    """Test data downsampling reduces points correctly"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/metrics/timeseries?points=5000&downsample=true")
        
        assert response.status_code == 200
        data = response.json()
        assert data["original_points"] == 5000
        assert data["returned_points"] <= 1920
        assert data["downsampled"] == True
