import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.anyio
async def test_root():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert "message" in data


@pytest.mark.anyio
async def test_vitals_rating():
    from app.services.metrics_service import _rate_vital
    assert _rate_vital("LCP", 1500) == "good"
    assert _rate_vital("LCP", 3000) == "needs-improvement"
    assert _rate_vital("LCP", 5000) == "poor"
    assert _rate_vital("CLS", 0.05) == "good"
    assert _rate_vital("CLS", 0.15) == "needs-improvement"
