import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import numpy as np
from scipy import stats
from sklearn.ensemble import IsolationForest
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.alert_rule import AlertRule, AlertInstance, RuleType, AlertState, AlertSeverity

logger = logging.getLogger(__name__)

@dataclass
class MetricPoint:
    timestamp: datetime
    value: float
    labels: Dict[str, str]

@dataclass
class EvaluationResult:
    rule_id: int
    triggered: bool
    value: float
    message: str
    severity: AlertSeverity
    labels: Dict[str, str]

class RuleEvaluator:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.anomaly_detectors = {}  # Cache for trained models
    
    async def evaluate_rule(self, rule: AlertRule, metric: MetricPoint, 
                          historical_data: List[MetricPoint]) -> Optional[EvaluationResult]:
        """Evaluate a single rule against a metric point."""
        try:
            if rule.rule_type == RuleType.THRESHOLD:
                return await self._evaluate_threshold_rule(rule, metric)
            elif rule.rule_type == RuleType.ANOMALY:
                return await self._evaluate_anomaly_rule(rule, metric, historical_data)
            elif rule.rule_type == RuleType.COMPOSITE:
                return await self._evaluate_composite_rule(rule, metric, historical_data)
        except Exception as e:
            logger.error(f"Error evaluating rule {rule.id}: {e}")
            return None
    
    async def _evaluate_threshold_rule(self, rule: AlertRule, metric: MetricPoint) -> Optional[EvaluationResult]:
        """Evaluate threshold-based rules."""
        conditions = rule.conditions
        value = metric.value
        
        # Support multiple threshold types
        if 'greater_than' in conditions:
            threshold = conditions['greater_than']
            triggered = value > threshold
            message = f"Value {value} exceeds threshold {threshold}"
        elif 'less_than' in conditions:
            threshold = conditions['less_than']
            triggered = value < threshold
            message = f"Value {value} below threshold {threshold}"
        elif 'between' in conditions:
            min_val, max_val = conditions['between']
            triggered = not (min_val <= value <= max_val)
            message = f"Value {value} outside range [{min_val}, {max_val}]"
        else:
            logger.warning(f"Unknown threshold condition for rule {rule.id}")
            return None
        
        if triggered:
            return EvaluationResult(
                rule_id=rule.id,
                triggered=True,
                value=value,
                message=message,
                severity=rule.severity,
                labels={**rule.labels, **metric.labels}
            )
        return None
    
    async def _evaluate_anomaly_rule(self, rule: AlertRule, metric: MetricPoint, 
                                   historical_data: List[MetricPoint]) -> Optional[EvaluationResult]:
        """Evaluate anomaly detection rules."""
        conditions = rule.conditions
        detection_type = conditions.get('type', 'statistical')
        
        if detection_type == 'statistical':
            return await self._statistical_anomaly_detection(rule, metric, historical_data)
        elif detection_type == 'isolation_forest':
            return await self._ml_anomaly_detection(rule, metric, historical_data)
        elif detection_type == 'seasonal':
            return await self._seasonal_anomaly_detection(rule, metric, historical_data)
        
        return None
    
    async def _statistical_anomaly_detection(self, rule: AlertRule, metric: MetricPoint, 
                                           historical_data: List[MetricPoint]) -> Optional[EvaluationResult]:
        """Statistical anomaly detection using Z-score."""
        if len(historical_data) < 30:  # Need sufficient data
            return None
        
        values = [point.value for point in historical_data]
        mean = np.mean(values)
        std = np.std(values)
        
        if std == 0:  # Avoid division by zero
            return None
        
        z_score = abs(metric.value - mean) / std
        threshold = rule.conditions.get('z_threshold', 3.0)
        
        if z_score > threshold:
            return EvaluationResult(
                rule_id=rule.id,
                triggered=True,
                value=metric.value,
                message=f"Statistical anomaly detected: Z-score {z_score:.2f} > {threshold}",
                severity=rule.severity,
                labels={**rule.labels, **metric.labels, 'z_score': str(round(z_score, 2))}
            )
        return None
    
    async def _ml_anomaly_detection(self, rule: AlertRule, metric: MetricPoint, 
                                  historical_data: List[MetricPoint]) -> Optional[EvaluationResult]:
        """Machine learning based anomaly detection."""
        if len(historical_data) < 100:  # Need more data for ML
            return None
        
        # Use cached model or train new one
        model_key = f"isolation_forest_{rule.id}"
        if model_key not in self.anomaly_detectors:
            values = np.array([[point.value] for point in historical_data])
            model = IsolationForest(contamination=0.1, random_state=42)
            model.fit(values)
            self.anomaly_detectors[model_key] = model
        
        model = self.anomaly_detectors[model_key]
        prediction = model.predict([[metric.value]])
        
        if prediction[0] == -1:  # Anomaly detected
            return EvaluationResult(
                rule_id=rule.id,
                triggered=True,
                value=metric.value,
                message=f"ML anomaly detected: Isolation Forest flagged value {metric.value}",
                severity=rule.severity,
                labels={**rule.labels, **metric.labels}
            )
        return None
    
    async def _seasonal_anomaly_detection(self, rule: AlertRule, metric: MetricPoint, 
                                        historical_data: List[MetricPoint]) -> Optional[EvaluationResult]:
        """Seasonal anomaly detection for time-series patterns."""
        if len(historical_data) < 168:  # Need at least 1 week of hourly data
            return None
        
        # Group by hour of day to find seasonal patterns
        hour_values = {}
        current_hour = metric.timestamp.hour
        
        for point in historical_data:
            hour = point.timestamp.hour
            if hour not in hour_values:
                hour_values[hour] = []
            hour_values[hour].append(point.value)
        
        if current_hour not in hour_values or len(hour_values[current_hour]) < 7:
            return None
        
        expected_values = hour_values[current_hour]
        mean = np.mean(expected_values)
        std = np.std(expected_values)
        
        if std == 0:
            return None
        
        deviation = abs(metric.value - mean) / std
        threshold = rule.conditions.get('seasonal_threshold', 2.5)
        
        if deviation > threshold:
            return EvaluationResult(
                rule_id=rule.id,
                triggered=True,
                value=metric.value,
                message=f"Seasonal anomaly: Value {metric.value} deviates {deviation:.2f}σ from hour {current_hour} average {mean:.2f}",
                severity=rule.severity,
                labels={**rule.labels, **metric.labels, 'expected': str(round(mean, 2))}
            )
        return None
    
    async def _evaluate_composite_rule(self, rule: AlertRule, metric: MetricPoint, 
                                     historical_data: List[MetricPoint]) -> Optional[EvaluationResult]:
        """Evaluate composite rules with multiple conditions."""
        # This would implement complex logic combining multiple conditions
        # For demo purposes, implementing a simple AND/OR logic
        conditions = rule.conditions
        results = []
        
        for condition in conditions.get('conditions', []):
            if condition['type'] == 'threshold':
                # Create temporary rule for evaluation
                temp_rule = AlertRule(
                    id=rule.id,
                    conditions=condition,
                    severity=rule.severity,
                    labels=rule.labels
                )
                result = await self._evaluate_threshold_rule(temp_rule, metric)
                results.append(result is not None)
        
        # Apply logical operator
        operator = conditions.get('operator', 'AND')
        if operator == 'AND':
            triggered = all(results)
        else:  # OR
            triggered = any(results)
        
        if triggered:
            return EvaluationResult(
                rule_id=rule.id,
                triggered=True,
                value=metric.value,
                message=f"Composite rule triggered: {operator} condition met",
                severity=rule.severity,
                labels={**rule.labels, **metric.labels}
            )
        return None

class AlertDeduplicator:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    async def should_generate_alert(self, result: EvaluationResult, 
                                  suppression_window: int = 300) -> bool:
        """Check if alert should be generated based on deduplication rules."""
        fingerprint = self._generate_fingerprint(result)
        
        # Check if we've seen this alert recently
        cache_key = f"alert_dedupe:{fingerprint}"
        existing = await self.redis.get(cache_key)
        
        if existing:
            # Alert already exists, check if we should suppress
            return False
        
        # Mark this alert as seen
        await self.redis.setex(cache_key, suppression_window, "1")
        return True
    
    def _generate_fingerprint(self, result: EvaluationResult) -> str:
        """Generate unique fingerprint for alert deduplication."""
        # Create fingerprint based on rule, labels, and severity
        fingerprint_data = {
            'rule_id': result.rule_id,
            'severity': result.severity.value,
            'labels': sorted(result.labels.items())
        }
        return str(hash(json.dumps(fingerprint_data, sort_keys=True)))

class EvaluationEngine:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.evaluator = RuleEvaluator(redis_client)
        self.deduplicator = AlertDeduplicator(redis_client)
        self.running = False
    
    async def start_evaluation_loop(self, db_session: AsyncSession):
        """Start the continuous evaluation loop."""
        self.running = True
        logger.info("Starting alert evaluation engine")
        
        while self.running:
            try:
                await self._evaluation_cycle(db_session)
                await asyncio.sleep(10)  # Evaluation interval
            except Exception as e:
                logger.error(f"Evaluation cycle error: {e}")
                await asyncio.sleep(30)  # Back off on error
    
    async def stop(self):
        """Stop the evaluation engine."""
        self.running = False
        logger.info("Stopping alert evaluation engine")
    
    async def _evaluation_cycle(self, db_session: AsyncSession):
        """Single evaluation cycle."""
        # In a real implementation, this would:
        # 1. Fetch active rules from database
        # 2. Get recent metrics from metrics system
        # 3. Evaluate each rule against relevant metrics
        # 4. Generate alerts for triggered rules
        # 5. Store alert instances in database
        
        # For demo, we'll simulate some activity
        logger.debug("Evaluation cycle executed")
