import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    
    assert response.status_code == 200
    assert "service" in response.json()
    print("✓ Root endpoint working")

def test_resources_endpoint():
    """Test resources endpoint"""
    response = client.get("/api/v1/resources/")
    
    assert response.status_code == 200
    print("✓ Resources endpoint working")

def test_costs_endpoint():
    """Test costs endpoint"""
    response = client.get("/api/v1/costs/summary")
    
    assert response.status_code == 200
    print("✓ Costs endpoint working")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
