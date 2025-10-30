import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))

from app.main import app

client = TestClient(app)

def test_create_user():
    response = client.post("/api/v1/users/", json={
        "username": "testuser",
        "email": "test@example.com",
        "timezone": "UTC"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    return data["id"]

def test_create_preferences():
    user_id = test_create_user()
    response = client.post("/api/v1/preferences/", json={
        "user_id": user_id,
        "global_quiet_hours_enabled": False
    })
    assert response.status_code == 200

def test_notification_processing():
    user_id = test_create_user()
    
    # Create preferences
    client.post("/api/v1/preferences/", json={
        "user_id": user_id,
        "global_quiet_hours_enabled": False
    })
    
    # Test notification simulation
    response = client.post("/api/v1/notifications/simulate", json={
        "user_id": user_id,
        "category": "security",
        "priority": "high",
        "title": "Test Alert",
        "message": "Test message"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "processing_result" in data

if __name__ == "__main__":
    test_create_user()
    test_create_preferences()
    test_notification_processing()
    print("✅ All tests passed!")
