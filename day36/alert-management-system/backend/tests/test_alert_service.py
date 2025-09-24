import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models.alert_models import AlertRule, AlertSeverity, AlertOperator
from app.services.alert_service import AlertService

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    Base.metadata.drop_all(bind=engine)

def test_create_alert_rule(db_session):
    service = AlertService(db_session)
    
    rule_data = {
        "name": "Test CPU Alert",
        "metric_name": "cpu.usage",
        "threshold_value": 80.0,
        "operator": AlertOperator.GREATER_THAN,
        "severity": AlertSeverity.WARNING
    }
    
    rule = service.create_alert_rule(rule_data)
    assert rule.id is not None
    assert rule.name == "Test CPU Alert"
    assert rule.threshold_value == 80.0

def test_evaluate_threshold(db_session):
    service = AlertService(db_session)
    
    rule = AlertRule(
        name="Test Rule",
        metric_name="test.metric",
        threshold_value=50.0,
        operator=AlertOperator.GREATER_THAN
    )
    
    assert service.evaluate_threshold(rule, 60.0) == True
    assert service.evaluate_threshold(rule, 40.0) == False
    assert service.evaluate_threshold(rule, 50.0) == False
