import pytest
import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "Server Authentication System" in response.json()["message"]

def test_create_ssh_key():
    key_data = {
        "name": "test-key",
        "key_type": "rsa",
        "expires_days": 90
    }
    response = client.post("/ssh-keys/", json=key_data)
    assert response.status_code == 200
    assert response.json()["name"] == "test-key"

def test_list_ssh_keys():
    response = client.get("/ssh-keys/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_dashboard_stats():
    response = client.get("/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_keys" in data
    assert "active_keys" in data
    assert "total_servers" in data
