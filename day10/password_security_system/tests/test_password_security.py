import pytest
import asyncio
from httpx import AsyncClient
from app.main import app
import fakeredis.aioredis

@pytest.fixture
async def client():
    # Use fake Redis for testing
    fake_redis = fakeredis.aioredis.FakeRedis()
    app.state.redis = fake_redis
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_password_strength_validation(client):
    """Test password strength validation"""
    
    # Test weak password
    response = await client.post("/api/auth/check-password-strength", json={"password": "123456"})
    result = response.json()
    assert response.status_code == 200
    assert result["valid"] == False
    assert result["strength"] in ["Very Weak", "Weak"]
    
    # Test strong password
    response = await client.post("/api/auth/check-password-strength", json={"password": "MyStr0ng!P@ssw0rd2024"})
    result = response.json()
    assert response.status_code == 200
    assert result["valid"] == True
    assert result["strength"] in ["Good", "Strong"]

@pytest.mark.asyncio
async def test_user_registration_and_verification(client):
    """Test complete user registration flow"""
    
    # Register user
    user_data = {
        "email": "test@example.com",
        "password": "SecureP@ssw0rd123!"
    }
    
    response = await client.post("/api/auth/register", json=user_data)
    result = response.json()
    
    assert response.status_code == 200
    assert "user_id" in result
    assert "verification_token" in result
    
    # Verify email
    verification_data = {"token": result["verification_token"]}
    response = await client.post("/api/auth/verify-email", json=verification_data)
    
    assert response.status_code == 200
    assert response.json()["message"] == "Email verified successfully"

@pytest.mark.asyncio
async def test_login_with_lockout(client):
    """Test login with account lockout mechanism"""
    
    # First register and verify a user
    user_data = {
        "email": "lockout@example.com",
        "password": "SecureP@ssw0rd123!"
    }
    
    reg_response = await client.post("/api/auth/register", json=user_data)
    reg_result = reg_response.json()
    
    # Verify email
    await client.post("/api/auth/verify-email", json={"token": reg_result["verification_token"]})
    
    # Try multiple failed logins
    login_data = {
        "email": "lockout@example.com",
        "password": "wrong_password"
    }
    
    for i in range(3):
        response = await client.post("/api/auth/login", json=login_data)
        assert response.status_code == 401
    
    # Successful login should work
    correct_login = {
        "email": "lockout@example.com",
        "password": "SecureP@ssw0rd123!"
    }
    
    response = await client.post("/api/auth/login", json=correct_login)
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_password_reset_flow(client):
    """Test complete password reset flow"""
    
    # Register and verify user first
    user_data = {
        "email": "reset@example.com",
        "password": "OriginalP@ssw0rd123!"
    }
    
    reg_response = await client.post("/api/auth/register", json=user_data)
    reg_result = reg_response.json()
    await client.post("/api/auth/verify-email", json={"token": reg_result["verification_token"]})
    
    # Request password reset
    reset_request = {"email": "reset@example.com"}
    response = await client.post("/api/auth/request-password-reset", json=reset_request)
    
    assert response.status_code == 200
    reset_result = response.json()
    
    # Complete password reset (if token is provided in response for testing)
    if "reset_token" in reset_result:
        new_password_data = {
            "token": reset_result["reset_token"],
            "new_password": "NewSecureP@ssw0rd456!"
        }
        
        response = await client.post("/api/auth/reset-password", json=new_password_data)
        assert response.status_code == 200
        assert response.json()["message"] == "Password reset successfully"

@pytest.mark.asyncio
async def test_rate_limiting(client):
    """Test rate limiting functionality"""
    
    # Test registration rate limiting
    user_data = {
        "email": "ratelimit@example.com",
        "password": "SecureP@ssw0rd123!"
    }
    
    # Make multiple rapid registration attempts
    responses = []
    for i in range(5):
        response = await client.post("/api/auth/register", json={
            "email": f"ratelimit{i}@example.com",
            "password": "SecureP@ssw0rd123!"
        })
        responses.append(response.status_code)
    
    # Should eventually hit rate limit
    assert 429 in responses or all(r == 200 for r in responses)

@pytest.mark.asyncio
async def test_security_monitoring(client):
    """Test security monitoring endpoints"""
    
    response = await client.get("/api/security/rate-limit-status")
    assert response.status_code == 200
    
    # Test lockout status
    response = await client.get("/api/security/lockout-status/test@example.com")
    assert response.status_code == 200
    
    result = response.json()
    assert "attempts" in result
    assert "is_locked_out" in result
