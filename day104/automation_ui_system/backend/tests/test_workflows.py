import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_workflow():
    response = client.post(
        "/api/v1/workflows",
        json={
            "name": "Test Workflow",
            "description": "Test workflow description",
            "definition": {
                "nodes": [
                    {"id": "1", "type": "http_request", "data": {"label": "API Call"}}
                ],
                "edges": []
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Workflow"
    assert "id" in data

def test_list_workflows():
    response = client.get("/api/v1/workflows")
    assert response.status_code == 200
    data = response.json()
    assert "workflows" in data
    assert isinstance(data["workflows"], list)

def test_get_workflow():
    create_response = client.post(
        "/api/v1/workflows",
        json={
            "name": "Test Workflow 2",
            "description": "Another test",
            "definition": {"nodes": [], "edges": []}
        }
    )
    workflow_id = create_response.json()["id"]
    response = client.get(f"/api/v1/workflows/{workflow_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == workflow_id
    assert data["name"] == "Test Workflow 2"
