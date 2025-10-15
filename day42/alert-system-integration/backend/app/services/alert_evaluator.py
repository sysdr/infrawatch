import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from ..models import Alert, AlertRule, AlertState, AlertSeverity, MetricData

logger = logging.getLogger(__name__)

class AlertEvaluator:
    def __init__(self, state_manager, notification_router):
        self.state_manager = state_manager
        self.notification_router = notification_router
        self.active_alerts: Dict[str, Alert] = {}
        self.evaluation_cache: Dict[str, tuple] = {}  # rule_id: (value, timestamp)
        self.cache_ttl = 10  # seconds
        
    async def evaluate_rule(self, rule: AlertRule, metrics: List[MetricData]) -> Optional[Alert]:
        """Evaluate a single alert rule against metrics"""
        if not rule.enabled:
            return None
            
        # Always get fresh metric value - don't use cache for now to ensure accuracy
        current_value = await self._get_current_metric_value(rule.metric, metrics)
        
        if current_value is None:
            return None
            
        # Evaluate condition
        threshold_breached = self._check_condition(current_value, rule.condition, rule.threshold)
        
        alert_key = rule.id
        existing_alert = self.active_alerts.get(alert_key)
        
        if threshold_breached:
            if existing_alert and existing_alert.state == AlertState.FIRING:
                # Update existing firing alert
                existing_alert.current_value = current_value
                existing_alert.updated_at = datetime.now()
                await self.state_manager.update_alert(existing_alert)
                return existing_alert
            elif existing_alert and existing_alert.state == AlertState.PENDING:
                # Check if pending duration exceeded
                if (datetime.now() - existing_alert.started_at).total_seconds() >= rule.duration:
                    existing_alert.state = AlertState.FIRING
                    existing_alert.updated_at = datetime.now()
                    await self.state_manager.update_alert(existing_alert)
                    await self.notification_router.route_notification(existing_alert)
                    return existing_alert
            else:
                # Create new alert in pending state
                alert = Alert(
                    id=alert_key,
                    rule_id=rule.id,
                    rule_name=rule.name,
                    state=AlertState.PENDING,
                    severity=rule.severity,
                    current_value=current_value,
                    threshold=rule.threshold,
                    started_at=datetime.now(),
                    updated_at=datetime.now(),
                    labels=rule.labels,
                    message=f"{rule.name}: {rule.metric} is {current_value} (threshold: {rule.threshold})"
                )
                self.active_alerts[alert_key] = alert
                await self.state_manager.add_alert(alert)
                return alert
        else:
            # Threshold not breached
            if existing_alert and existing_alert.state in [AlertState.FIRING, AlertState.PENDING]:
                # Resolve the alert
                existing_alert.state = AlertState.RESOLVED
                existing_alert.resolved_at = datetime.now()
                existing_alert.updated_at = datetime.now()
                await self.state_manager.update_alert(existing_alert)
                await self.notification_router.send_resolution_notification(existing_alert)
                del self.active_alerts[alert_key]
                return existing_alert
                
        return None
    
    async def _get_current_metric_value(self, metric: str, metrics: List[MetricData]) -> Optional[float]:
        """Get the most recent value for a metric"""
        matching_metrics = [m for m in metrics if m.metric == metric]
        if not matching_metrics:
            return None
        latest = max(matching_metrics, key=lambda m: m.timestamp)
        return latest.value
    
    def _check_condition(self, value: float, condition: str, threshold: float) -> bool:
        """Check if a condition is met"""
        conditions = {
            '>': lambda v, t: v > t,
            '<': lambda v, t: v < t,
            '>=': lambda v, t: v >= t,
            '<=': lambda v, t: v <= t,
            '==': lambda v, t: abs(v - t) < 0.001,
        }
        return conditions.get(condition, lambda v, t: False)(value, threshold)
    
    async def evaluate_all_rules(self, rules: List[AlertRule], metrics: List[MetricData]):
        """Evaluate all rules against current metrics"""
        tasks = [self.evaluate_rule(rule, metrics) for rule in rules]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        evaluated_alerts = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Error evaluating rule: {result}")
            elif result:
                evaluated_alerts.append(result)
        
        return evaluated_alerts
