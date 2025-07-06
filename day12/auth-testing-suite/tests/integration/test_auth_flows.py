import pytest
from httpx import AsyncClient

@pytest.mark.integration
class TestAuthFlows:
    
    async def test_complete_registration_flow(self, async_client: AsyncClient):
        # 1. Register
        register_response = await async_client.post("/api/auth/register", json={
            "email": "flow@example.com", 
            "password": "FlowTest123!",
            "first_name": "Flow",
            "last_name": "Test"
        })
        
        assert register_response.status_code == 201
        tokens = register_response.json()
        
        # 2. Access protected route
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        profile_response = await async_client.get("/api/auth/profile", headers=headers)
        
        assert profile_response.status_code == 200
        assert profile_response.json()["email"] == "flow@example.com"
        
        # 3. Logout
        logout_response = await async_client.post("/api/auth/logout", 
            headers=headers,
            json={"refresh_token": tokens["refresh_token"]}
        )
        assert logout_response.status_code == 200
    
    async def test_token_refresh_flow(self, async_client: AsyncClient, test_user):
        # 1. Login
        login_response = await async_client.post("/api/auth/login", json={
            "email": test_user.email,
            "password": "TestPass123!"
        })
        
        tokens = login_response.json()
        refresh_token = tokens["refresh_token"]
        
        # 2. Refresh tokens
        refresh_response = await async_client.post("/api/auth/refresh", 
            json={"refresh_token": refresh_token})
        
        assert refresh_response.status_code == 200
        new_tokens = refresh_response.json()
        assert new_tokens["access_token"] != tokens["access_token"]
        assert new_tokens["refresh_token"] != refresh_token
        
        # 3. Use new access token
        headers = {"Authorization": f"Bearer {new_tokens['access_token']}"}
        profile_response = await async_client.get("/api/auth/profile", headers=headers)
        assert profile_response.status_code == 200 