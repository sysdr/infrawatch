import pytest
import httpx
import asyncio

BASE_URL = "http://localhost:8117"

@pytest.mark.asyncio
async def test_health_endpoint():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/api/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"

@pytest.mark.asyncio
async def test_list_users():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/api/users?page=1&limit=10")
    assert r.status_code == 200
    data = r.json()
    assert "users" in data
    assert len(data["users"]) <= 10

@pytest.mark.asyncio
async def test_list_teams():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/api/teams")
    assert r.status_code == 200
    data = r.json()
    assert "teams" in data

@pytest.mark.asyncio
async def test_start_load_test():
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{BASE_URL}/api/tests/start", json={
            "name": "Integration Test Run",
            "test_type": "load",
            "target_url": BASE_URL,
            "users": 3,
            "duration_seconds": 8,
        })
    assert r.status_code == 200
    data = r.json()
    assert "run_id" in data
    assert data["status"] == "started"

@pytest.mark.asyncio
async def test_start_benchmark():
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{BASE_URL}/api/tests/start", json={
            "name": "Benchmark Integration",
            "test_type": "benchmark",
            "target_url": BASE_URL,
        })
    assert r.status_code == 200
    data = r.json()
    assert "run_id" in data

@pytest.mark.asyncio
async def test_list_runs():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/api/tests/runs")
    assert r.status_code == 200
    data = r.json()
    assert "runs" in data
    assert isinstance(data["runs"], list)

@pytest.mark.asyncio
async def test_system_metrics():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/api/system/metrics")
    assert r.status_code == 200
    data = r.json()
    assert "cpu_percent" in data
    assert "memory_percent" in data

@pytest.mark.asyncio
async def test_dashboard_stats():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/api/dashboard/stats")
    assert r.status_code == 200
    data = r.json()
    assert "total_users" in data
    assert "total_teams" in data
