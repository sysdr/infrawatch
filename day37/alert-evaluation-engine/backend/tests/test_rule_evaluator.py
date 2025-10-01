import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock
import redis.asyncio as redis

from src.services.rule_evaluator import RuleEvaluator, MetricPoint, EvaluationResult
from src.models.alert_rule import AlertRule, RuleType, AlertSeverity

@pytest.mark.asyncio
class TestRuleEvaluator:
    
    @pytest.fixture
    async def redis_client(self):
        # Use fakeredis for testing
        import fakeredis.aioredis
        return fakeredis.aioredis.FakeRedis()
    
    @pytest.fixture
    def evaluator(self, redis_client):
        return RuleEvaluator(redis_client)
    
    @pytest.fixture
    def threshold_rule(self):
        rule = Mock(spec=AlertRule)
        rule.id = 1
        rule.rule_type = RuleType.THRESHOLD
        rule.conditions = {'greater_than': 80.0}
        rule.severity = AlertSeverity.WARNING
        rule.labels = {'service': 'web'}
        return rule
    
    @pytest.fixture
    def anomaly_rule(self):
        rule = Mock(spec=AlertRule)
        rule.id = 2
        rule.rule_type = RuleType.ANOMALY
        rule.conditions = {'type': 'statistical', 'z_threshold': 3.0}
        rule.severity = AlertSeverity.CRITICAL
        rule.labels = {'service': 'database'}
        return rule
    
    async def test_threshold_rule_triggers_when_exceeded(self, evaluator, threshold_rule):
        metric = MetricPoint(
            timestamp=datetime.utcnow(),
            value=85.0,
            labels={'instance': 'web-01'}
        )
        
        result = await evaluator.evaluate_rule(threshold_rule, metric, [])
        
        assert result is not None
        assert result.triggered is True
        assert result.value == 85.0
        assert result.severity == AlertSeverity.WARNING
        assert 'exceeds threshold' in result.message
    
    async def test_threshold_rule_does_not_trigger_when_below(self, evaluator, threshold_rule):
        metric = MetricPoint(
            timestamp=datetime.utcnow(),
            value=75.0,
            labels={'instance': 'web-01'}
        )
        
        result = await evaluator.evaluate_rule(threshold_rule, metric, [])
        
        assert result is None
    
    async def test_statistical_anomaly_detection(self, evaluator, anomaly_rule):
        # Create normal historical data
        historical_data = []
        for i in range(50):
            historical_data.append(MetricPoint(
                timestamp=datetime.utcnow() - timedelta(minutes=i),
                value=50.0 + (i % 5),  # Normal range 50-54
                labels={'instance': 'db-01'}
            ))
        
        # Test with anomalous value
        metric = MetricPoint(
            timestamp=datetime.utcnow(),
            value=100.0,  # Clear anomaly
            labels={'instance': 'db-01'}
        )
        
        result = await evaluator.evaluate_rule(anomaly_rule, metric, historical_data)
        
        assert result is not None
        assert result.triggered is True
        assert result.severity == AlertSeverity.CRITICAL
        assert 'Statistical anomaly' in result.message
    
    async def test_insufficient_historical_data_for_anomaly(self, evaluator, anomaly_rule):
        # Insufficient historical data
        historical_data = [
            MetricPoint(datetime.utcnow(), 50.0, {})
        ]
        
        metric = MetricPoint(datetime.utcnow(), 100.0, {})
        
        result = await evaluator.evaluate_rule(anomaly_rule, metric, historical_data)
        
        assert result is None  # Should not trigger with insufficient data
