import pytest
from fastapi.testclient import TestClient
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_get_users():
    response = client.get("/api/users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_user():
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "avatar": "https://i.pravatar.cc/150"
    }
    response = client.post("/api/users", json=user_data)
    assert response.status_code == 200
    assert response.json()["email"] == user_data["email"]

def test_get_teams():
    response = client.get("/api/teams")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_roles():
    response = client.get("/api/roles")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_activities():
    response = client.get("/api/activities")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
