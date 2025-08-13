import pytest
from httpx import AsyncClient
from app.models.server import Server, ServerStatus

@pytest.mark.asyncio
async def test_create_server(async_client):
    server_data = {
        "name": "test-server-1",
        "description": "Test server description",
        "ip_address": "192.168.1.100",
        "port": 8080
    }
    
    response = await async_client.post("/api/v1/servers/", json=server_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == server_data["name"]
    assert data["data"]["status"] == "creating"

@pytest.mark.asyncio
async def test_list_servers(async_client):
    response = await async_client.get("/api/v1/servers/")
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)

@pytest.mark.asyncio
async def test_update_server_status(async_client):
    # First create a server
    server_data = {"name": "test-server-status", "description": "Status test"}
    create_response = await async_client.post("/api/v1/servers/", json=server_data)
    server_id = create_response.json()["data"]["id"]
    
    # Update status
    response = await async_client.put(f"/api/v1/servers/{server_id}/status?status=running")
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "running"

@pytest.mark.asyncio
async def test_delete_server(async_client):
    # First create a server
    server_data = {"name": "test-server-delete", "description": "Delete test"}
    create_response = await async_client.post("/api/v1/servers/", json=server_data)
    server_id = create_response.json()["data"]["id"]
    
    # Delete server
    response = await async_client.delete(f"/api/v1/servers/{server_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True

@pytest.mark.asyncio
async def test_get_nonexistent_server(async_client):
    response = await async_client.get("/api/v1/servers/99999")
    assert response.status_code == 404
