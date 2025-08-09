import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_get_servers():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/servers/")
    assert response.status_code == 200
    data = response.json()
    assert "servers" in data
    assert "total" in data

@pytest.mark.asyncio  
async def test_create_server():
    server_data = {
        "name": "Test Server",
        "hostname": "test.example.com",
        "ip_address": "192.168.1.100",
        "server_type": "web"
    }
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/servers/", json=server_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Server"
    assert data["hostname"] == "test.example.com"

@pytest.mark.asyncio
async def test_server_metrics():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/servers/metrics")
    
    assert response.status_code == 200
    data = response.json()
    assert "total_servers" in data
    assert "healthy_count" in data
