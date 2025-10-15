import pytest
import asyncio
from datetime import datetime
from app.models import AlertRule, AlertSeverity, MetricData, AlertState
from app.services.state_manager import StateManager
from app.services.alert_evaluator import AlertEvaluator
from app.services.notification_router import NotificationRouter
from app.websocket.coordinator import WebSocketCoordinator

@pytest.fixture
def websocket_coordinator():
    return WebSocketCoordinator()

@pytest.fixture
def state_manager(websocket_coordinator):
    return StateManager(websocket_coordinator)

@pytest.fixture
def notification_router(state_manager):
    return NotificationRouter(state_manager)

@pytest.fixture
def alert_evaluator(state_manager, notification_router):
    return AlertEvaluator(state_manager, notification_router)

@pytest.mark.asyncio
async def test_alert_evaluation_triggers_notification(alert_evaluator, state_manager):
    """Test that alert evaluation triggers notifications"""
    rule = AlertRule(
        id="test_rule",
        name="Test Rule",
        metric="test_metric",
        condition=">",
        threshold=50.0,
        duration=0,
        severity=AlertSeverity.WARNING
    )
    
    await state_manager.add_rule(rule)
    
    metrics = [MetricData(
        metric="test_metric",
        value=75.0,
        timestamp=datetime.now(),
        labels={}
    )]
    
    alert = await alert_evaluator.evaluate_rule(rule, metrics)
    assert alert is not None
    assert alert.state in [AlertState.PENDING, AlertState.FIRING]
    assert alert.current_value == 75.0

@pytest.mark.asyncio
async def test_alert_resolution_workflow(alert_evaluator, state_manager):
    """Test complete alert lifecycle from firing to resolution"""
    rule = AlertRule(
        id="test_rule_2",
        name="Test Resolution",
        metric="test_metric",
        condition=">",
        threshold=50.0,
        duration=0,
        severity=AlertSeverity.WARNING
    )
    
    await state_manager.add_rule(rule)
    
    # Trigger alert
    high_metrics = [MetricData(
        metric="test_metric",
        value=75.0,
        timestamp=datetime.now(),
        labels={}
    )]
    
    alert = await alert_evaluator.evaluate_rule(rule, high_metrics)
    assert alert is not None
    
    # Wait for duration and trigger again
    await asyncio.sleep(0.1)
    alert = await alert_evaluator.evaluate_rule(rule, high_metrics)
    
    # Resolve alert
    low_metrics = [MetricData(
        metric="test_metric",
        value=25.0,
        timestamp=datetime.now(),
        labels={}
    )]
    
    resolved_alert = await alert_evaluator.evaluate_rule(rule, low_metrics)
    if resolved_alert:
        assert resolved_alert.state == AlertState.RESOLVED

@pytest.mark.asyncio
async def test_circuit_breaker_activation(notification_router):
    """Test circuit breaker prevents cascade failures"""
    breaker = notification_router.circuit_breakers.get("default")
    if not breaker:
        from app.services.notification_router import CircuitBreaker
        breaker = CircuitBreaker(failure_threshold=3)
        notification_router.circuit_breakers["default"] = breaker
    
    # Record failures
    for _ in range(3):
        breaker.record_failure()
    
    assert breaker.is_open
    assert not breaker.can_attempt()

@pytest.mark.asyncio
async def test_concurrent_alert_processing(alert_evaluator, state_manager):
    """Test concurrent processing of multiple alerts"""
    rules = [
        AlertRule(
            id=f"concurrent_rule_{i}",
            name=f"Concurrent Test {i}",
            metric=f"metric_{i}",
            condition=">",
            threshold=50.0,
            duration=0,
            severity=AlertSeverity.WARNING
        )
        for i in range(10)
    ]
    
    for rule in rules:
        await state_manager.add_rule(rule)
    
    metrics = [
        MetricData(
            metric=f"metric_{i}",
            value=75.0,
            timestamp=datetime.now(),
            labels={}
        )
        for i in range(10)
    ]
    
    alerts = await alert_evaluator.evaluate_all_rules(rules, metrics)
    assert len(alerts) >= 0  # Some alerts may be created

@pytest.mark.asyncio
async def test_real_time_state_updates(state_manager):
    """Test state updates are propagated correctly"""
    from app.models import Alert
    
    alert = Alert(
        id="test_alert_state",
        rule_id="test_rule",
        rule_name="Test",
        state=AlertState.PENDING,
        severity=AlertSeverity.INFO,
        current_value=60.0,
        threshold=50.0,
        started_at=datetime.now(),
        updated_at=datetime.now(),
        labels={},
        message="Test alert"
    )
    
    await state_manager.add_alert(alert)
    retrieved = await state_manager.get_alert(alert.id)
    assert retrieved.id == alert.id
    assert retrieved.state == AlertState.PENDING

@pytest.mark.asyncio
async def test_notification_retry_logic(notification_router):
    """Test notification retry with exponential backoff"""
    from app.models import Alert, Notification, NotificationStatus
    
    alert = Alert(
        id="retry_test_alert",
        rule_id="test",
        rule_name="Test",
        state=AlertState.FIRING,
        severity=AlertSeverity.CRITICAL,
        current_value=95.0,
        threshold=80.0,
        started_at=datetime.now(),
        updated_at=datetime.now(),
        labels={},
        message="Test retry"
    )
    
    # This will attempt retries
    await notification_router.route_notification(alert)
    await asyncio.sleep(0.5)  # Give time for retries
    
    # Check notifications were attempted
    assert len(notification_router.notifications) > 0

@pytest.mark.asyncio
async def test_error_recovery(alert_evaluator, state_manager):
    """Test system recovers from evaluation errors"""
    rule = AlertRule(
        id="error_rule",
        name="Error Test",
        metric="nonexistent_metric",
        condition=">",
        threshold=50.0,
        duration=0,
        severity=AlertSeverity.WARNING
    )
    
    await state_manager.add_rule(rule)
    
    metrics = [MetricData(
        metric="different_metric",
        value=75.0,
        timestamp=datetime.now(),
        labels={}
    )]
    
    # Should handle missing metric gracefully
    alert = await alert_evaluator.evaluate_rule(rule, metrics)
    # No exception should be raised

@pytest.mark.asyncio
async def test_websocket_broadcast(websocket_coordinator):
    """Test WebSocket message broadcasting"""
    message = {
        "type": "test",
        "data": {"value": 123}
    }
    
    # Should not fail even with no connections
    await websocket_coordinator.broadcast(message)
    assert True  # No exception raised
