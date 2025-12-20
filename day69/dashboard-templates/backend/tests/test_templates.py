import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app import models

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_create_template():
    response = client.post("/api/v1/templates", json={
        "name": "Test Template",
        "description": "Test description",
        "config": {
            "widgets": [
                {"id": "w1", "type": "chart", "title": "CPU {{service_name}}"}
            ]
        },
        "visibility": "private",
        "category": "monitoring",
        "tags": ["test", "monitoring"],
        "variables": [
            {
                "name": "service_name",
                "description": "Service to monitor",
                "variable_type": "string",
                "required": True
            }
        ]
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Template"
    assert data["version"] == "1.0.0"
    assert data["status"] == "draft"

def test_search_templates():
    # Create a template first
    client.post("/api/v1/templates", json={
        "name": "Monitoring Template",
        "description": "CPU and Memory monitoring",
        "config": {"widgets": []},
        "category": "monitoring",
        "tags": ["infrastructure"]
    })
    
    # Publish it
    db = next(override_get_db())
    template = db.query(models.Template).first()
    template.status = "published"
    db.commit()
    
    response = client.get("/api/v1/templates?query=monitoring")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1

def test_template_versioning():
    # Create template
    response = client.post("/api/v1/templates", json={
        "name": "Test Template",
        "description": "Test",
        "config": {"widgets": [{"id": "w1"}]},
        "category": "test"
    })
    template_id = response.json()["id"]
    
    # Update with new config (should create new version)
    response = client.put(f"/api/v1/templates/{template_id}", json={
        "config": {"widgets": [{"id": "w1"}, {"id": "w2"}]}
    })
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "1.1.0"  # Minor version bump

def test_template_instantiation():
    # Create and publish template
    response = client.post("/api/v1/templates", json={
        "name": "Service Dashboard",
        "config": {
            "widgets": [
                {"id": "w1", "title": "{{service_name}} CPU"}
            ]
        },
        "category": "monitoring"
    })
    template_id = response.json()["id"]
    
    # Publish
    db = next(override_get_db())
    template = db.query(models.Template).filter(models.Template.id == template_id).first()
    template.status = "published"
    db.commit()
    
    # Instantiate
    response = client.post(f"/api/v1/templates/{template_id}/instantiate", json={
        "name": "My Dashboard",
        "variable_values": {"service_name": "api-service"}
    })
    assert response.status_code == 200
    data = response.json()
    assert "api-service" in str(data["config"])

def test_template_rating():
    # Create and publish template
    response = client.post("/api/v1/templates", json={
        "name": "Test Template",
        "config": {"widgets": []},
        "category": "test"
    })
    template_id = response.json()["id"]
    
    db = next(override_get_db())
    template = db.query(models.Template).filter(models.Template.id == template_id).first()
    template.status = "published"
    db.commit()
    
    # Rate
    response = client.post(f"/api/v1/templates/{template_id}/rate", json={
        "rating": 5,
        "review": "Excellent template"
    })
    assert response.status_code == 200
    
    # Check template rating updated
    response = client.get(f"/api/v1/templates/{template_id}")
    data = response.json()
    assert data["rating"] == 5
    assert data["rating_count"] == 1
