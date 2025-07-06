import pytest
from httpx import AsyncClient

class TestAuthControllers:
    
    async def test_register_endpoint(self, async_client: AsyncClient):
        user_data = {
            "email": "unit@example.com",
            "password": "UnitTest123!",
            "first_name": "Unit",
            "last_name": "Test"
        }
        
        response = await async_client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["user"]["email"] == user_data["email"]
        assert "access_token" in data
        assert "refresh_token" in data
    
    async def test_login_endpoint(self, async_client: AsyncClient, test_user):
        response = await async_client.post("/api/auth/login", json={
            "email": test_user.email,
            "password": "TestPass123!"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["email"] == test_user.email
        assert "access_token" in data
        assert "refresh_token" in data
    
    async def test_login_invalid_credentials(self, async_client: AsyncClient, test_user):
        response = await async_client.post("/api/auth/login", json={
            "email": test_user.email,
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
    
    async def test_profile_endpoint(self, async_client: AsyncClient, test_user):
        # Login first
        login_response = await async_client.post("/api/auth/login", json={
            "email": test_user.email,
            "password": "TestPass123!"
        })
        
        tokens = login_response.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        response = await async_client.get("/api/auth/profile", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert "password" not in data
        assert "hashed_password" not in data 