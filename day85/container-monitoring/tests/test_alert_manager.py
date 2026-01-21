import pytest
from datetime import datetime
from backend.services.alert_manager import AlertManager
from backend.models.container import Alert, ContainerHealth, ContainerEvent


def test_alert_manager_initialization():
    """Test AlertManager initialization"""
    manager = AlertManager()
    assert manager.get_active_alerts() == []


def test_add_alert():
    """Test adding an alert"""
    manager = AlertManager()
    alert = Alert(
        container_id="test123",
        container_name="test-container",
        timestamp=datetime.utcnow(),
        alert_type="cpu",
        severity="warning",
        message="CPU usage high",
        current_value=85.0,
        threshold=80.0
    )
    manager.add_alert(alert)
    
    alerts = manager.get_active_alerts()
    assert len(alerts) > 0
    assert alerts[0].alert_type == "cpu"


def test_duplicate_alert_prevention():
    """Test that duplicate alerts are prevented"""
    manager = AlertManager()
    alert = Alert(
        container_id="test123",
        container_name="test-container",
        timestamp=datetime.utcnow(),
        alert_type="cpu",
        severity="warning",
        message="CPU usage high",
        current_value=85.0,
        threshold=80.0
    )
    
    # Add same alert twice
    manager.add_alert(alert)
    initial_count = len(manager.get_active_alerts())
    
    # Add again immediately (should be prevented)
    manager.add_alert(alert)
    final_count = len(manager.get_active_alerts())
    
    # Should not have increased
    assert final_count == initial_count


def test_health_alert():
    """Test health check alert generation"""
    manager = AlertManager()
    health = ContainerHealth(
        container_id="test123",
        container_name="test-container",
        timestamp=datetime.utcnow(),
        status="unhealthy",
        failing_streak=3
    )
    
    alert = manager.check_health_alert(health)
    assert alert is not None
    assert alert.alert_type == "health"
    assert alert.severity == "critical"


def test_restart_tracking():
    """Test container restart tracking"""
    manager = AlertManager()
    
    # Simulate multiple restarts
    for i in range(6):
        event = ContainerEvent(
            container_id="test123",
            container_name="test-container",
            timestamp=datetime.utcnow(),
            action="restart",
            status="restart"
        )
        alert = manager.track_restart(event)
        
        if i >= 4:  # After 5 restarts
            assert alert is not None
            assert alert.alert_type == "restart"
            assert alert.severity == "critical"


def test_clear_alerts():
    """Test clearing alerts for a container"""
    manager = AlertManager()
    alert = Alert(
        container_id="test123",
        container_name="test-container",
        timestamp=datetime.utcnow(),
        alert_type="cpu",
        severity="warning",
        message="CPU usage high",
        current_value=85.0,
        threshold=80.0
    )
    manager.add_alert(alert)
    
    assert len(manager.get_active_alerts("test123")) > 0
    manager.clear_alerts("test123")
    assert len(manager.get_active_alerts("test123")) == 0
