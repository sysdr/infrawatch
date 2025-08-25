import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Metrics Storage & Retrieval System"

def test_health():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()

def test_metrics_summary():
    """Test metrics summary endpoint"""
    response = client.get("/metrics/summary")
    assert response.status_code == 200
    assert "summary" in response.json()
