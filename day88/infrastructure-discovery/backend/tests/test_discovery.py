import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_discovery_scan():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/discovery/scan")
        assert response.status_code == 200
        data = response.json()
        assert "resources_discovered" in data

@pytest.mark.asyncio
async def test_inventory_list():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/inventory/resources")
        assert response.status_code == 200
        data = response.json()
        assert "resources" in data

@pytest.mark.asyncio
async def test_topology_graph():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/topology/graph")
        assert response.status_code == 200
        data = response.json()
        assert "nodes" in data
        assert "links" in data

@pytest.mark.asyncio
async def test_changes_recent():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/changes/recent?hours=1")
        assert response.status_code == 200
        data = response.json()
        assert "changes" in data
