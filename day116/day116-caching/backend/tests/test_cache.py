import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
os.environ.setdefault("REDIS_URL", "redis://localhost:6379")
from app.main import app

@pytest_asyncio.fixture
async def client():
    # Run app lifespan so app.state.cache is set (required for routes)
    async with app.router.lifespan_context(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            yield ac
@pytest.mark.asyncio
async def test_health(client): r = await client.get("/health"); assert r.status_code == 200; assert r.json()["status"] == "ok"
@pytest.mark.asyncio
async def test_cache_set_get(client):
    await client.post("/api/cache/set", json={"key": "t:k", "value": {"x": 1}, "ttl": 60, "tags": [], "strategy": "ttl"})
    r = await client.get("/api/cache/get/t:k"); assert r.json()["hit"] is True
