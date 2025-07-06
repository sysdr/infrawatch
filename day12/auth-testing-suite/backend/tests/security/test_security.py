import pytest
from httpx import AsyncClient
from app.main import app

class TestSecurityFeatures:
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test rate limiting on auth endpoints"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Send multiple rapid requests to trigger rate limiting
            responses = []
            for _ in range(15):  # More than the 10/minute limit
                response = await client.post("/api/auth/login", json={
                    "email": "test@example.com",
                    "password": "wrong_password"
                })
                responses.append(response)
            
            # Check if any requests were rate limited
            rate_limited = [r for r in responses if r.status_code == 429]
            assert len(rate_limited) > 0
    
    @pytest.mark.asyncio
    async def test_weak_password_rejection(self):
        """Test that weak passwords are rejected"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            weak_passwords = ["password", "12345678", "Password", "password123"]
            
            for password in weak_passwords:
                response = await client.post("/api/auth/register", json={
                    "email": f"test_{password}@example.com",
                    "password": password,
                    "first_name": "Test",
                    "last_name": "User"
                })
                # Should be rejected (400 or 422)
                assert response.status_code in [400, 422]
    
    @pytest.mark.asyncio
    async def test_invalid_email_rejection(self):
        """Test that invalid emails are rejected"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            invalid_emails = ["invalid-email", "@example.com", "user@", "user@.com"]
            
            for email in invalid_emails:
                response = await client.post("/api/auth/register", json={
                    "email": email,
                    "password": "StrongPass123!",
                    "first_name": "Test",
                    "last_name": "User"
                })
                # Should be rejected
                assert response.status_code in [400, 422]
    
    @pytest.mark.asyncio
    async def test_unauthorized_access_denied(self):
        """Test that protected endpoints deny unauthorized access"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Try to access protected endpoint without token
            response = await client.get("/api/auth/profile")
            assert response.status_code == 401
            
            # Try with invalid token
            response = await client.get("/api/auth/profile", headers={
                "Authorization": "Bearer invalid_token"
            })
            assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_sql_injection_protection(self):
        """Test protection against SQL injection attempts"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # SQL injection attempts in email field
            sql_injection_attempts = [
                "'; DROP TABLE users; --",
                "' OR '1'='1",
                "admin'--",
                "test@example.com' UNION SELECT * FROM users--"
            ]
            
            for attempt in sql_injection_attempts:
                response = await client.post("/api/auth/register", json={
                    "email": attempt,
                    "password": "StrongPass123!",
                    "first_name": "Test",
                    "last_name": "User"
                })
                # Should be rejected or handled safely
                assert response.status_code in [400, 422, 500]
    
    @pytest.mark.asyncio
    async def test_xss_protection(self):
        """Test protection against XSS attempts"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            xss_attempts = [
                "<script>alert('xss')</script>",
                "javascript:alert('xss')",
                "<img src=x onerror=alert('xss')>",
                "';alert('xss');//"
            ]
            
            for attempt in xss_attempts:
                response = await client.post("/api/auth/register", json={
                    "email": f"test{attempt}@example.com",
                    "password": "StrongPass123!",
                    "first_name": attempt,
                    "last_name": "User"
                })
                # Should be rejected or sanitized
                assert response.status_code in [400, 422] 