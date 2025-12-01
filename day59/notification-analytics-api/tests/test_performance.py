import pytest
import time
from httpx import AsyncClient
from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app

@pytest.mark.asyncio
async def test_chart_endpoint_performance():
    """Test chart endpoint response time"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        start = time.time()
        response = await client.get("/api/analytics/chart", params={
            "metric": "event_count",
            "group_by": "channel",
            "start": (datetime.utcnow() - timedelta(days=1)).isoformat(),
            "end": datetime.utcnow().isoformat()
        })
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 0.5  # Should respond in < 500ms
        print(f"Chart endpoint response time: {elapsed*1000:.2f}ms")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--benchmark"])
