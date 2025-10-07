import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.database import Base, get_db
from app.main import app

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_alert_rules.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_db():
    """Clean database before each test"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_create_rule():
    """Test rule creation"""
    rule_data = {
        "name": "Test CPU Alert",
        "description": "Test CPU utilization alert",
        "expression": "avg(cpu_usage_percent) > {threshold}",
        "severity": "warning",
        "enabled": True,
        "tags": ["infrastructure", "cpu"],
        "thresholds": {"threshold": 85}
    }
    
    response = client.post("/api/v1/rules/", json=rule_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == rule_data["name"]
    assert data["expression"] == rule_data["expression"]

def test_get_rules():
    """Test getting all rules"""
    response = client.get("/api/v1/rules/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_rule_validation():
    """Test rule validation"""
    # Test invalid expression
    invalid_rule = {
        "name": "Invalid Rule",
        "expression": "",  # Empty expression
        "thresholds": {"threshold": 85}
    }
    
    response = client.post("/api/v1/rules/", json=invalid_rule)
    assert response.status_code == 422

def test_template_creation():
    """Test template creation"""
    template_data = {
        "name": "Test Template",
        "description": "Test CPU template",
        "category": "infrastructure",
        "template_config": {
            "expression": "avg(cpu_usage_percent) > {threshold}",
            "thresholds": {"threshold": 85},
            "severity": "warning",
            "tags": ["infrastructure"]
        }
    }
    
    response = client.post("/api/v1/templates/", json=template_data)
    assert response.status_code == 200

def test_rule_testing():
    """Test rule testing functionality"""
    test_data = {
        "rule_config": {
            "name": "Test Rule",
            "expression": "avg(cpu_usage_percent) > {threshold}",
            "severity": "warning",
            "thresholds": {"threshold": 85},
            "tags": [],
            "enabled": True
        },
        "test_data": [
            {"cpu_usage_percent": 45.2},
            {"cpu_usage_percent": 89.7}
        ],
        "expected_results": [False, True]
    }
    
    response = client.post("/api/v1/test/rule", json=test_data)
    assert response.status_code == 200
    data = response.json()
    assert "total_tests" in data
    assert data["total_tests"] == 2

if __name__ == "__main__":
    pytest.main([__file__])
