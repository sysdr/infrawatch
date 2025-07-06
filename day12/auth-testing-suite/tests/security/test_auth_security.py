import pytest
from httpx import AsyncClient

@pytest.mark.security
class TestPasswordSecurity:
    
    @pytest.mark.parametrize("weak_password", [
        "password", "12345678", "Password", "password123", "PASSWORD123"
    ])
    async def test_weak_passwords_rejected(self, async_client: AsyncClient, weak_password):
        response = await async_client.post("/api/auth/register", json={
            "email": "test@example.com",
            "password": weak_password,
            "first_name": "Test",
            "last_name": "User"
        })
        assert response.status_code == 422
        
    async def test_strong_password_accepted(self, async_client: AsyncClient):
        response = await async_client.post("/api/auth/register", json={
            "email": "test@example.com",
            "password": "StrongPass123!",
            "first_name": "Test",
            "last_name": "User"
        })
        assert response.status_code == 201

@pytest.mark.security
class TestAccountLockout:
    
    async def test_account_lockout_after_failed_attempts(self, async_client: AsyncClient, test_user):
        # Make 5 failed attempts
        for _ in range(5):
            await async_client.post("/api/auth/login", json={
                "email": test_user.email,
                "password": "wrongpassword"
            })
        
        # 6th attempt should return locked status
        response = await async_client.post("/api/auth/login", json={
            "email": test_user.email,
            "password": "wrongpassword"
        })
        assert response.status_code == 423
        assert "locked" in response.json()["detail"].lower()

@pytest.mark.security  
class TestJWTSecurity:
    
    async def test_invalid_jwt_rejected(self, async_client: AsyncClient):
        response = await async_client.get("/api/auth/profile", 
            headers={"Authorization": "Bearer invalid.jwt.token"})
        assert response.status_code == 401
        
    async def test_malformed_jwt_rejected(self, async_client: AsyncClient):
        response = await async_client.get("/api/auth/profile",
            headers={"Authorization": "Bearer malformed_token"})
        assert response.status_code == 401 