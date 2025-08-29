import pytest
import asyncio
from httpx import AsyncClient
from datetime import datetime, timedelta
from app.main import app

@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health check endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/metrics/health")
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data

@pytest.mark.asyncio
async def test_list_metrics():
    """Test metrics listing endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/metrics/list")
    
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "count" in data

@pytest.mark.asyncio
async def test_query_metrics():
    """Test metrics query endpoint"""
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=1)
    
    params = {
        "metric_name": "cpu_usage_percent",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "interval": "5m",
        "aggregations": ["avg"]
    }
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/metrics/query", params=params)
    
    assert response.status_code == 200
    data = response.json()
    assert "metric_name" in data
    assert "data_points" in data
    assert "total_points" in data

@pytest.mark.asyncio
async def test_export_json():
    """Test JSON export functionality"""
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=1)
    
    params = {
        "metric_name": "cpu_usage_percent",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "format": "json"
    }
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/metrics/export", params=params)
    
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "metadata" in data

@pytest.mark.asyncio
async def test_export_csv():
    """Test CSV export functionality"""
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=1)
    
    params = {
        "metric_name": "cpu_usage_percent",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "format": "csv"
    }
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/metrics/export", params=params)
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
