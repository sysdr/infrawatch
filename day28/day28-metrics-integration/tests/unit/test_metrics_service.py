import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from app.services.metrics_service import MetricsService
from app.schemas.metrics import MetricCreate, MetricQuery
import json

class TestMetricsService:
    
    @pytest.fixture
    def metrics_service(self):
        return MetricsService()
    
    @pytest.fixture
    def mock_db_session(self):
        session = AsyncMock()
        return session
    
    @pytest.fixture
    def sample_metric(self):
        return MetricCreate(
            name="test_metric",
            value=42.5,
            source="test_source",
            tags={"environment": "test"}
        )
    
    async def test_create_metric(self, metrics_service, mock_db_session, sample_metric):
        """Test creating a single metric"""
        # Mock database entry
        mock_db_metric = MagicMock()
        mock_db_metric.id = 1
        mock_db_metric.name = sample_metric.name
        mock_db_metric.value = sample_metric.value
        mock_db_metric.source = sample_metric.source
        mock_db_metric.timestamp = "2024-01-01T12:00:00"
        
        mock_db_session.add = MagicMock()
        mock_db_session.flush = AsyncMock()
        mock_db_session.refresh = AsyncMock()
        
        # Mock Redis service
        import app.services.metrics_service
        app.services.metrics_service.redis_service.set_metric = AsyncMock(return_value=True)
        
        result = await metrics_service.create_metric(mock_db_session, sample_metric)
        
        # Verify database operations
        mock_db_session.add.assert_called_once()
        mock_db_session.flush.assert_called_once()
        mock_db_session.refresh.assert_called_once()
        
        # Verify Redis operation
        app.services.metrics_service.redis_service.set_metric.assert_called_once()
    
    async def test_create_metrics_batch(self, metrics_service, mock_db_session):
        """Test creating multiple metrics in batch"""
        metrics = [
            MetricCreate(
                name=f"batch_metric_{i}",
                value=float(i * 10),
                source="batch_source",
                tags={"batch": "test"}
            )
            for i in range(3)
        ]
        
        mock_db_session.add_all = MagicMock()
        mock_db_session.flush = AsyncMock()
        
        # Mock Redis service
        import app.services.metrics_service
        app.services.metrics_service.redis_service.set_metric = AsyncMock(return_value=True)
        
        result = await metrics_service.create_metrics_batch(mock_db_session, metrics)
        
        # Verify batch operations
        mock_db_session.add_all.assert_called_once()
        mock_db_session.flush.assert_called_once()
        
        # Verify Redis operations (should be called for each metric)
        assert app.services.metrics_service.redis_service.set_metric.call_count == 3
    
    async def test_query_metrics_with_filters(self, metrics_service, mock_db_session):
        """Test querying metrics with various filters"""
        query = MetricQuery(
            name="test_metric",
            source="test_source",
            limit=10,
            offset=0
        )
        
        # Mock database result
        mock_result = MagicMock()
        mock_metrics = [MagicMock() for _ in range(5)]
        mock_result.scalars.return_value.all.return_value = mock_metrics
        
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        result = await metrics_service.query_metrics(mock_db_session, query)
        
        # Verify query execution
        mock_db_session.execute.assert_called_once()
        
        # Verify filters were applied (check the SQL statement construction)
        call_args = mock_db_session.execute.call_args[0][0]
        # The actual SQL checking would be more complex in a real test
        assert result is not None
    
    async def test_get_realtime_metrics(self, metrics_service):
        """Test getting realtime metrics from Redis"""
        expected_metrics = {
            "metric:cpu_usage:server1:123456": {
                "name": "cpu_usage",
                "value": 75.5,
                "source": "server1"
            }
        }
        
        # Mock Redis service
        import app.services.metrics_service
        app.services.metrics_service.redis_service.get_latest_metrics = AsyncMock(
            return_value=expected_metrics
        )
        
        result = await metrics_service.get_realtime_metrics()
        
        assert result == expected_metrics
        app.services.metrics_service.redis_service.get_latest_metrics.assert_called_once()
    
    async def test_get_metric_summary(self, metrics_service, mock_db_session):
        """Test getting statistical summary for a metric"""
        # Mock database result
        mock_result = MagicMock()
        mock_summary = MagicMock()
        mock_summary.min_value = 10.0
        mock_summary.max_value = 90.0
        mock_summary.avg_value = 50.0
        mock_summary.count = 100
        
        mock_result.first.return_value = mock_summary
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        result = await metrics_service.get_metric_summary(
            mock_db_session, "test_metric", 24
        )
        
        expected = {
            "name": "test_metric",
            "min_value": 10.0,
            "max_value": 90.0,
            "avg_value": 50.0,
            "count": 100,
            "period_hours": 24
        }
        
        assert result == expected
        mock_db_session.execute.assert_called_once()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
