import pytest
from fastapi.testclient import TestClient
from backend.app.core.app import create_app

@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_ecommerce_workflow(client):
    """Test creating e-commerce sample workflow"""
    response = client.post("/api/v1/workflows/samples/ecommerce")
    assert response.status_code == 200
    
    data = response.json()
    assert "workflow_id" in data
    assert data["status"] == "created"
    assert data["type"] == "ecommerce"

def test_create_blog_workflow(client):
    """Test creating blog sample workflow"""
    response = client.post("/api/v1/workflows/samples/blog")
    assert response.status_code == 200
    
    data = response.json()
    assert "workflow_id" in data
    assert data["status"] == "created"
    assert data["type"] == "blog"

def test_list_workflows(client):
    """Test listing workflows"""
    # Create a workflow first
    client.post("/api/v1/workflows/samples/ecommerce")
    
    response = client.get("/api/v1/workflows")
    assert response.status_code == 200
    
    data = response.json()
    assert "workflows" in data
    assert len(data["workflows"]) > 0

def test_workflow_status(client):
    """Test getting workflow status"""
    # Create a workflow first
    create_response = client.post("/api/v1/workflows/samples/ecommerce")
    workflow_id = create_response.json()["workflow_id"]
    
    response = client.get(f"/api/v1/workflows/{workflow_id}/status")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == workflow_id
    assert "tasks" in data
    assert len(data["tasks"]) > 0

def test_execute_workflow(client):
    """Test workflow execution"""
    # Create a workflow first
    create_response = client.post("/api/v1/workflows/samples/ecommerce")
    workflow_id = create_response.json()["workflow_id"]
    
    response = client.post(f"/api/v1/workflows/{workflow_id}/execute")
    assert response.status_code == 200
    
    data = response.json()
    assert data["workflow_id"] == workflow_id
    assert data["status"] == "started"

def test_metrics_endpoint(client):
    """Test metrics endpoint"""
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    
    data = response.json()
    assert "total_tasks" in data
    assert "success_rate" in data

if __name__ == "__main__":
    pytest.main([__file__])
