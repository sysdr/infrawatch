import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from app.services.alert_service import AlertQueryService
from app.models.alert_models import Alert, AlertStatus, AlertSeverity

class TestAlertQueryService:
    def test_search_alerts_basic(self):
        # Mock database session
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 5
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []
        
        service = AlertQueryService(mock_db)
        result = service.search_alerts(query="test")
        
        assert result["total_count"] == 5
        assert "alerts" in result
        assert "page" in result

    def test_get_alert_statistics(self):
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        
        # Mock status stats
        mock_query.group_by.return_value = mock_query
        mock_query.all.return_value = [
            Mock(status="active", count=10),
            Mock(status="resolved", count=20)
        ]
        
        service = AlertQueryService(mock_db)
        
        with patch.object(service.db, 'query') as mock_query_method:
            mock_query_method.return_value.group_by.return_value.all.return_value = [
                Mock(status="active", count=10)
            ]
            mock_query_method.return_value.count.return_value = 30
            mock_query_method.return_value.filter.return_value.count.return_value = 10
            
            stats = service.get_alert_statistics()
            
            assert "status_distribution" in stats
            assert "total_alerts" in stats
            assert "active_alerts" in stats

    def test_bulk_update_alerts(self):
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [Mock(id=1), Mock(id=2)]
        mock_query.update.return_value = 2
        
        service = AlertQueryService(mock_db)
        result = service.bulk_update_alerts([1, 2], {"status": "resolved"})
        
        assert result["success"] is True
        assert result["updated_count"] == 2

if __name__ == "__main__":
    pytest.main([__file__])
