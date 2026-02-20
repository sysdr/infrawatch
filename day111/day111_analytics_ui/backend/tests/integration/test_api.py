import pytest
import pytest_asyncio
import httpx

BASE_URL = "http://localhost:8000/api/v1"

@pytest.mark.asyncio
async def test_health():
    async with httpx.AsyncClient() as client:
        r = await client.get("http://localhost:8000/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_dashboard_returns_kpis():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/analytics/dashboard")
    assert r.status_code == 200
    data = r.json()
    assert "kpis" in data
    assert len(data["kpis"]) > 0
    kpi = data["kpis"][0]
    assert "name" in kpi
    assert "value" in kpi
    assert "sparkline" in kpi

@pytest.mark.asyncio
async def test_ml_predict():
    features = {
        "cpu_utilization": 92.0,
        "memory_usage": 88.0,
        "request_latency_ms": 350.0,
        "error_rate": 2.5,
        "throughput_rps": 400.0,
        "queue_depth": 55.0,
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{BASE_URL}/ml/predict", json={"features": features})
    assert r.status_code == 200
    result = r.json()
    assert "prediction" in result
    assert result["prediction"] in ["anomaly", "normal"]
    assert 0.0 <= result["probability"] <= 1.0
    assert "feature_importance" in result

@pytest.mark.asyncio
async def test_correlation():
    payload = {
        "metrics": ["cpu_utilization", "memory_usage", "request_latency_ms", "error_rate"],
        "time_window_hours": 2,
        "method": "pearson"
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{BASE_URL}/analytics/correlate", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "matrix" in data
    assert len(data["matrix"]) == 4
    assert len(data["labels"]) == 4

@pytest.mark.asyncio
async def test_report_create_and_export():
    payload = {
        "name": "Test Report",
        "config": {"metrics": ["cpu_utilization", "memory_usage"]},
        "output_format": "csv"
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{BASE_URL}/reports/", json=payload)
    assert r.status_code == 200
    report_id = r.json()["id"]

    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/reports/{report_id}/export/csv")
    assert r.status_code == 200
    assert b"metric_name" in r.content

@pytest.mark.asyncio
async def test_config_update():
    async with httpx.AsyncClient() as client:
        r = await client.patch(f"{BASE_URL}/config/",
                               json={"key": "refresh_interval_seconds", "value": 10})
    assert r.status_code == 200
    assert r.json()["value"] == 10
