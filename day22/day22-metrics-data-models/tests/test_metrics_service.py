import pytest
import sys
import os
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from models.metrics import Base
from services.metrics_service import MetricsService

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture
def metrics_service(db_session):
    return MetricsService(db_session)

def test_store_metric(metrics_service, db_session):
    """Test storing a single metric"""
    
    metric_data = {
        'metric_name': 'test.cpu.usage',
        'metric_type': 'gauge',
        'value': 75.5,
        'timestamp': datetime.now(timezone.utc),
        'tags': {'host': 'web-01', 'env': 'test'}
    }
    
    metric_id = metrics_service.store_metric(metric_data)
    db_session.commit()
    
    assert metric_id is not None
    assert len(metric_id) > 0

def test_query_metrics(metrics_service, db_session):
    """Test querying metrics"""
    
    # Store test data
    metric_data = {
        'metric_name': 'test.response.time',
        'metric_type': 'gauge',
        'value': 150.0,
        'timestamp': datetime.now(timezone.utc),
        'tags': {'service': 'api'}
    }
    
    metrics_service.store_metric(metric_data)
    db_session.commit()
    
    # Query data
    end_time = datetime.now(timezone.utc) + timedelta(minutes=1)
    start_time = datetime.now(timezone.utc) - timedelta(minutes=1)
    
    results = metrics_service.query_metrics(
        'test.response.time', 
        start_time, 
        end_time
    )
    
    assert len(results) == 1
    assert results[0]['value'] == 150.0

def test_search_metrics(metrics_service, db_session):
    """Test metric search functionality"""
    
    # Store test metrics
    metrics = [
        {'metric_name': 'cpu.usage', 'value': 50.0, 'metric_type': 'gauge'},
        {'metric_name': 'memory.usage', 'value': 60.0, 'metric_type': 'gauge'},
        {'metric_name': 'disk.io', 'value': 70.0, 'metric_type': 'counter'}
    ]
    
    for metric in metrics:
        metric['timestamp'] = datetime.now(timezone.utc)
        metrics_service.store_metric(metric)
    
    db_session.commit()
    
    # Search for metrics
    results = metrics_service.search_metrics('usage')
    
    assert len(results) == 2
    names = [r['name'] for r in results]
    assert 'cpu.usage' in names
    assert 'memory.usage' in names
