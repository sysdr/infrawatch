import pytest
from httpx import AsyncClient, ASGITransport
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.main import app
from app.ml.pipeline import MLPipeline

@pytest.fixture(autouse=True)
def reset_pipeline():
    MLPipeline._instance = None
    yield
    MLPipeline._instance = None

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_train_pipeline():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/v1/ml/train?n_samples=200")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "trained"
    assert data["training_samples"] == 200

@pytest.mark.asyncio
async def test_full_pipeline_flow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        train_resp = await client.post("/api/v1/ml/train?n_samples=200")
        assert train_resp.status_code == 200
        anomaly_resp = await client.get("/api/v1/ml/anomalies/latest")
        assert anomaly_resp.status_code == 200
        assert "anomaly" in anomaly_resp.json()
        forecast_resp = await client.get("/api/v1/ml/forecast?metric=cpu_usage")
        assert forecast_resp.status_code == 200
        assert "forecast" in forecast_resp.json()
