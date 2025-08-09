import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json

from app.main import app
from app.database import get_db, Base

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Server API Enhancement" in response.json()["message"]

def test_search_servers():
    # Test basic search
    response = client.post("/api/servers/search", json={
        "filters": [],
        "page": 1,
        "page_size": 20
    })
    assert response.status_code == 200
    data = response.json()
    assert "servers" in data
    assert "total" in data

def test_server_groups():
    # Create a group
    group_data = {
        "name": "Test Group",
        "description": "Test group description",
        "color": "#FF0000"
    }
    response = client.post("/api/server-groups", json=group_data)
    assert response.status_code == 200
    
    # List groups
    response = client.get("/api/server-groups")
    assert response.status_code == 200
    groups = response.json()
    assert len(groups) >= 1

def test_templates():
    # Create a template
    template_data = {
        "name": "Test Template",
        "description": "Test template",
        "config": {
            "instance_type": "t3.micro",
            "region": "us-east-1",
            "cpu_cores": 2,
            "memory_gb": 4
        }
    }
    response = client.post("/api/templates", json=template_data)
    assert response.status_code == 200
    
    # List templates
    response = client.get("/api/templates")
    assert response.status_code == 200
    templates = response.json()
    assert len(templates) >= 1

def test_bulk_operations():
    # Test bulk action request
    bulk_data = {
        "action": "start",
        "server_ids": [1, 2, 3],
        "parameters": {}
    }
    response = client.post("/api/servers/bulk-action", json=bulk_data)
    assert response.status_code == 200
    result = response.json()
    assert "task_id" in result
