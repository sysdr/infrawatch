import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_create_dashboard():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/dashboards/", json={
            "name": "Test Dashboard",
            "description": "A test dashboard",
            "layout": []
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Dashboard"
        assert "id" in data

@pytest.mark.asyncio
async def test_get_dashboards():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/dashboards/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
