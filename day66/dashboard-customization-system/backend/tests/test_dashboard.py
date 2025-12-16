import pytest
from httpx import AsyncClient
from app.main import app
from app.database import init_db
import asyncio

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    await init_db()

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def auth_token(client):
    # Register and login
    register_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123"
    }
    await client.post("/api/auth/register", json=register_data)
    
    login_data = {"email": "test@example.com", "password": "testpass123"}
    response = await client.post("/api/auth/login", json=login_data)
    return response.json()["access_token"]

@pytest.mark.asyncio
async def test_create_dashboard(client, auth_token):
    dashboard_data = {
        "name": "Test Dashboard",
        "description": "Test description",
        "config": {
            "layout": [
                {
                    "widget_id": "w1",
                    "widget_type": "timeseries",
                    "position": [0, 0, 4, 3],
                    "config": {"metric": "cpu_usage"}
                }
            ],
            "metadata": {}
        },
        "theme": "light"
    }
    
    response = await client.post(
        "/api/dashboards",
        json=dashboard_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Dashboard"
    assert data["version"] == 1

@pytest.mark.asyncio
async def test_update_dashboard(client, auth_token):
    # Create dashboard first
    dashboard_data = {
        "name": "Test Dashboard",
        "config": {"layout": [], "metadata": {}},
        "theme": "light"
    }
    
    create_response = await client.post(
        "/api/dashboards",
        json=dashboard_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    dashboard_id = create_response.json()["id"]
    
    # Update dashboard
    update_data = {
        "name": "Updated Dashboard",
        "version": 1
    }
    
    response = await client.put(
        f"/api/dashboards/{dashboard_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Dashboard"
    assert data["version"] == 2

@pytest.mark.asyncio
async def test_create_share(client, auth_token):
    # Create dashboard
    dashboard_data = {
        "name": "Shared Dashboard",
        "config": {"layout": [], "metadata": {}},
        "theme": "light"
    }
    
    create_response = await client.post(
        "/api/dashboards",
        json=dashboard_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    dashboard_id = create_response.json()["id"]
    
    # Create share
    share_data = {"permission": "view", "expires_in_hours": 24}
    response = await client.post(
        f"/api/dashboards/{dashboard_id}/share",
        json=share_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["permission"] == "view"
    assert "share_token" in data
