import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_register_user():
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "password": "testpassword123"
    }
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert "tokens" in data
    assert data["user"]["email"] == user_data["email"]

def test_login_user():
    # First register a user
    user_data = {
        "email": "login@example.com",
        "username": "loginuser",
        "password": "loginpassword123"
    }
    client.post("/api/auth/register", json=user_data)
    
    # Then login
    login_data = {
        "email": "login@example.com",
        "password": "loginpassword123"
    }
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "tokens" in data
    assert data["tokens"]["access_token"] is not None

def test_protected_endpoint():
    # Register and login to get token
    user_data = {
        "email": "protected@example.com",
        "username": "protecteduser",
        "password": "protectedpassword123"
    }
    register_response = client.post("/api/auth/register", json=user_data)
    token = register_response.json()["tokens"]["access_token"]
    
    # Access protected endpoint
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/users/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == user_data["email"]

def test_invalid_login():
    login_data = {
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    }
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 401
