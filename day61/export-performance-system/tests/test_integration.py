import pytest
import asyncio
import httpx

BASE_URL = "http://localhost:8000"

@pytest.mark.asyncio
async def test_export_performance():
    """Test export with performance monitoring"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/exports/notifications",
            params={'user_id': 'user1', 'format': 'json'}
        )
        assert response.status_code == 200
        data = response.json()
        assert 'execution_time_ms' in data
        assert data['execution_time_ms'] < 1000  # Should be under 1 second

@pytest.mark.asyncio
async def test_cache_hit():
    """Test cache hit on repeated request"""
    async with httpx.AsyncClient() as client:
        # First request - cache miss
        response1 = await client.post(
            f"{BASE_URL}/api/exports/notifications",
            params={'user_id': 'user2', 'format': 'json'}
        )
        assert response1.json()['cached'] == False
        
        # Second request - should hit cache
        response2 = await client.post(
            f"{BASE_URL}/api/exports/notifications",
            params={'user_id': 'user2', 'format': 'json'}
        )
        assert response2.json()['cached'] == True
        assert response2.json()['execution_time_ms'] < 50  # Cache should be fast

@pytest.mark.asyncio
async def test_performance_metrics():
    """Test performance metrics endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/performance/metrics")
        assert response.status_code == 200
        data = response.json()
        assert 'query_times' in data
        assert 'exports' in data

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
