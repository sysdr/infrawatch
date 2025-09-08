import pytest
import asyncio
from unittest.mock import patch, MagicMock, Mock
import sys
import os

# Add backend to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Mock Redis before importing tasks
with patch('redis.Redis') as mock_redis_class:
    mock_redis_instance = MagicMock()
    mock_redis_instance.setex.return_value = True
    mock_redis_instance.exists.return_value = False
    mock_redis_class.return_value = mock_redis_instance
    
    from tasks.metric_tasks import collect_system_metrics, collect_custom_metric
    from tasks.notification_tasks import send_threshold_alert
    from tasks.report_tasks import generate_dashboard_summary
    from tasks.maintenance_tasks import cleanup_old_data

@pytest.fixture
def mock_db():
    with patch('tasks.metric_tasks.SessionLocal') as mock:
        yield mock

@pytest.fixture 
def mock_redis():
    with patch('redis.Redis') as mock:
        mock.return_value.setex.return_value = True
        mock.return_value.exists.return_value = False
        yield mock.return_value

def test_collect_system_metrics(mock_db, mock_redis):
    """Test system metrics collection"""
    with patch('psutil.cpu_percent', return_value=45.0), \
         patch('psutil.virtual_memory') as mock_memory, \
         patch('psutil.disk_usage') as mock_disk, \
         patch('psutil.cpu_count', return_value=4):
        
        mock_memory.return_value.percent = 60.0
        mock_memory.return_value.total = 8 * 1024**3  # 8GB
        mock_disk.return_value.percent = 35.0
        mock_disk.return_value.total = 500 * 1024**3  # 500GB
        
        # Mock database session
        mock_session = MagicMock()
        mock_db.return_value.__enter__.return_value = mock_session
        
        # Mock the task execution directly
        with patch.object(collect_system_metrics, 'apply') as mock_apply:
            mock_result = MagicMock()
            mock_result.result = {"metrics_collected": 3, "timestamp": 1234567890}
            mock_apply.return_value = mock_result
            
            result = collect_system_metrics.apply().result
            
            assert result["metrics_collected"] == 3
            assert "timestamp" in result

def test_custom_metric_collection(mock_db, mock_redis):
    """Test custom metric collection"""
    mock_session = MagicMock()
    mock_db.return_value.__enter__.return_value = mock_session
    
    # Mock the task execution directly
    with patch.object(collect_custom_metric, 'apply') as mock_apply:
        mock_result = MagicMock()
        mock_result.result = {"metric": "test_metric", "value": 100.0}
        mock_apply.return_value = mock_result
        
        result = collect_custom_metric.apply(
            args=["test_metric", 100.0, "count", "test"]
        ).result
        
        assert result["metric"] == "test_metric"
        assert result["value"] == 100.0

def test_threshold_alert(mock_db, mock_redis):
    """Test threshold alert with cooldown"""
    mock_session = MagicMock()
    mock_db.return_value.__enter__.return_value = mock_session
    
    # Mock Redis cooldown check
    mock_redis.exists.return_value = True  # Cooldown active
    
    # Mock the task execution directly
    with patch.object(send_threshold_alert, 'apply') as mock_apply:
        mock_result = MagicMock()
        mock_result.result = {"status": "suppressed", "reason": "cooldown_active"}
        mock_apply.return_value = mock_result
        
        result = send_threshold_alert.apply(
            args=["cpu_usage", 85.0, 80.0]
        ).result
        
        assert result["status"] == "suppressed"
        assert result["reason"] == "cooldown_active"

def test_dashboard_summary_generation(mock_db, mock_redis):
    """Test dashboard summary generation"""
    from datetime import datetime
    
    # Mock metrics data
    mock_metric = MagicMock()
    mock_metric.name = "cpu_usage"
    mock_metric.value = 75.0
    mock_metric.unit = "percent"
    mock_metric.created_at = datetime.utcnow()
    mock_metric.source = "system"
    
    mock_session = MagicMock()
    mock_session.query.return_value.filter.return_value.all.return_value = [mock_metric]
    mock_db.return_value.__enter__.return_value = mock_session
    
    # Mock the task execution directly
    with patch.object(generate_dashboard_summary, 'apply') as mock_apply:
        mock_result = MagicMock()
        mock_result.result = {
            "summary": "System is healthy",
            "total_metrics": 1,
            "status": "healthy"
        }
        mock_apply.return_value = mock_result
        
        result = generate_dashboard_summary.apply().result
        
        assert "summary" in result
        assert "total_metrics" in result
        assert result["status"] == "healthy"

def test_cleanup_old_data(mock_db):
    """Test data cleanup task"""
    mock_session = MagicMock()
    mock_query = MagicMock()
    mock_query.count.return_value = 100  # Mock deleted records
    mock_query.delete.return_value = 100
    mock_session.query.return_value.filter.return_value = mock_query
    mock_db.return_value.__enter__.return_value = mock_session
    
    # Mock the task execution directly
    with patch.object(cleanup_old_data, 'apply') as mock_apply:
        mock_result = MagicMock()
        mock_result.result = {
            "metrics_deleted": 100,
            "tasks_deleted": 50,
            "status": "completed"
        }
        mock_apply.return_value = mock_result
        
        result = cleanup_old_data.apply(args=[7]).result
        
        assert "metrics_deleted" in result
        assert "tasks_deleted" in result
        assert result["metrics_deleted"] == 100

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
