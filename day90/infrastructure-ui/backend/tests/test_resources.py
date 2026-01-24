import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_list_resources():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/resources")
        assert response.status_code == 200
        data = response.json()
        assert 'items' in data
        assert 'total' in data
