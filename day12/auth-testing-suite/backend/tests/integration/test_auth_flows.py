import pytest
from httpx import AsyncClient
from app.main import app

class TestAuthFlows:
    
    @pytest.mark.asyncio
    async def test_complete_registration_flow(self):
        """Test complete user registration flow"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Register new user
            register_data = {
                "email": "integration@example.com",
                "password": "IntegrationTest123!",
                "first_name": "Integration",
                "last_name": "Test"
            }
            
            response = await client.post("/api/auth/register", json=register_data)
            assert response.status_code == 201
            
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data
            assert data["user"]["email"] == register_data["email"]
    
    @pytest.mark.asyncio
    async def test_login_flow(self):
        """Test user login flow"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # First register a user
            register_data = {
                "email": "login@example.com",
                "password": "LoginTest123!",
                "first_name": "Login",
                "last_name": "Test"
            }
            
            await client.post("/api/auth/register", json=register_data)
            
            # Then login
            login_data = {
                "email": "login@example.com",
                "password": "LoginTest123!"
            }
            
            response = await client.post("/api/auth/login", json=login_data)
            assert response.status_code == 200
            
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data
    
    @pytest.mark.asyncio
    async def test_protected_endpoint_access(self):
        """Test access to protected endpoints"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Register and get tokens
            register_data = {
                "email": "protected@example.com",
                "password": "ProtectedTest123!",
                "first_name": "Protected",
                "last_name": "Test"
            }
            
            register_response = await client.post("/api/auth/register", json=register_data)
            tokens = register_response.json()
            
            # Access protected endpoint
            headers = {"Authorization": f"Bearer {tokens['access_token']}"}
            response = await client.get("/api/auth/profile", headers=headers)
            assert response.status_code == 200
            
            profile_data = response.json()
            assert profile_data["email"] == register_data["email"]
    
    @pytest.mark.asyncio
    async def test_logout_flow(self):
        """Test user logout flow"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Register and get tokens
            register_data = {
                "email": "logout@example.com",
                "password": "LogoutTest123!",
                "first_name": "Logout",
                "last_name": "Test"
            }
            
            register_response = await client.post("/api/auth/register", json=register_data)
            tokens = register_response.json()
            
            # Logout
            headers = {"Authorization": f"Bearer {tokens['access_token']}"}
            logout_data = {"refresh_token": tokens["refresh_token"]}
            
            response = await client.post("/api/auth/logout", json=logout_data, headers=headers)
            assert response.status_code == 200 