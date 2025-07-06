import pytest
import time
import asyncio
from httpx import AsyncClient

@pytest.mark.performance
class TestResponseTimes:
    
    async def test_login_response_time(self, async_client: AsyncClient, test_user):
        start_time = time.time()
        
        response = await async_client.post("/api/auth/login", json={
            "email": test_user.email,
            "password": "TestPass123!"
        })
        
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        
        assert response.status_code == 200
        assert response_time < 1000  # Less than 1 second
    
    async def test_registration_response_time(self, async_client: AsyncClient):
        start_time = time.time()
        
        response = await async_client.post("/api/auth/register", json={
            "email": "perf@example.com",
            "password": "PerfTest123!",
            "first_name": "Perf",
            "last_name": "Test"
        })
        
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        
        assert response.status_code == 201
        assert response_time < 2000  # Less than 2 seconds

@pytest.mark.performance
class TestConcurrentUsers:
    
    async def test_concurrent_logins(self, async_client: AsyncClient):
        # Create test users first
        users = []
        for i in range(10):
            user_data = {
                "email": f"user{i}@example.com",
                "password": "TestPass123!",
                "first_name": f"User{i}",
                "last_name": "Test"
            }
            await async_client.post("/api/auth/register", json=user_data)
            users.append(user_data)
        
        # Concurrent login attempts
        login_tasks = [
            async_client.post("/api/auth/login", json={
                "email": user["email"],
                "password": user["password"]
            })
            for user in users
        ]
        
        start_time = time.time()
        responses = await asyncio.gather(*login_tasks)
        end_time = time.time()
        
        successful_logins = [r for r in responses if r.status_code == 200]
        total_time = (end_time - start_time) * 1000
        
        assert len(successful_logins) == 10
        assert total_time < 3000  # Less than 3 seconds for 10 concurrent logins 