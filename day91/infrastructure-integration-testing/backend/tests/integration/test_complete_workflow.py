"""Complete workflow integration tests"""
import pytest
from httpx import AsyncClient
from datetime import datetime
import asyncio

@pytest.mark.asyncio
async def test_discovery_to_monitoring_flow():
    """Test resource discovery flows into monitoring"""
    async with AsyncClient(base_url="http://localhost:8000") as client:
        # Get discovered resources
        response = await client.get("/api/v1/discovery/resources")
        assert response.status_code == 200
        resources = response.json()
        assert len(resources) > 0
        
        # Verify monitoring is active
        response = await client.get("/api/v1/monitoring/metrics")
        assert response.status_code == 200
        metrics = response.json()
        assert metrics["total_metrics"] > 0

@pytest.mark.asyncio
async def test_monitoring_to_cost_tracking():
    """Test monitoring data flows into cost tracking"""
    async with AsyncClient(base_url="http://localhost:8000") as client:
        # Get monitoring metrics
        response = await client.get("/api/v1/monitoring/metrics")
        assert response.status_code == 200
        
        # Get cost summary
        response = await client.get("/api/v1/costs/summary")
        assert response.status_code == 200
        cost_data = response.json()
        assert cost_data["total_monthly_cost"] > 0

@pytest.mark.asyncio
async def test_end_to_end_integration():
    """Test complete end-to-end integration"""
    async with AsyncClient(base_url="http://localhost:8000") as client:
        # Run integration test
        test_request = {
            "test_type": "end_to_end",
            "cloud_provider": "aws",
            "resource_count": 10,
            "duration_minutes": 5,
            "chaos_enabled": False
        }
        
        response = await client.post("/api/v1/integration/tests/run", json=test_request)
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "started"
        test_id = result["test_id"]
        
        # Wait for test completion
        await asyncio.sleep(10)
        
        # Get test results
        response = await client.get(f"/api/v1/integration/tests/{test_id}")
        assert response.status_code == 200
        test_result = response.json()
        assert test_result["status"] in ["completed", "running"]
