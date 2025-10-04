import pytest
import asyncio
from backend.app.services.alert_processor import AlertProcessor
from backend.app.models.alert import Alert, AlertState, AlertSeverity

@pytest.fixture
def sample_alert_data():
    return {
        'title': 'Test Alert',
        'description': 'Test alert description',
        'metric_name': 'cpu_usage',
        'service_name': 'test-service',
        'current_value': 90.0,
        'threshold_value': 80.0
    }

@pytest.mark.asyncio
async def test_alert_processing(sample_alert_data):
    processor = AlertProcessor()
    await processor.start()
    
    # Test alert creation
    alert = await processor.process_alert(sample_alert_data)
    assert alert.state == AlertState.NEW
    assert alert.severity in AlertSeverity
    
    # Test acknowledgment
    acknowledged_alert = await processor.acknowledge_alert(alert.id, 'test_user')
    assert acknowledged_alert.state == AlertState.ACKNOWLEDGED
    assert acknowledged_alert.acknowledged_by == 'test_user'
    
    # Test resolution
    resolved_alert = await processor.resolve_alert(alert.id, 'test_user')
    assert resolved_alert.state == AlertState.RESOLVED
    assert resolved_alert.resolved_by == 'test_user'
    
    await processor.stop()

@pytest.mark.asyncio
async def test_severity_classification(sample_alert_data):
    processor = AlertProcessor()
    
    # Test critical service
    sample_alert_data['service_name'] = 'database'
    sample_alert_data['current_value'] = 200.0  # High breach ratio
    
    alert = Alert(**sample_alert_data)
    severity = await processor._classify_severity(alert)
    
    assert severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]

def test_alert_model():
    alert = Alert(
        title='Test Alert',
        metric_name='cpu_usage',
        service_name='test-service',
        current_value=90.0,
        threshold_value=80.0
    )
    
    alert_dict = alert.to_dict()
    assert alert_dict['title'] == 'Test Alert'
    assert alert_dict['state'] == 'NEW'
    assert alert_dict['current_value'] == 90.0
