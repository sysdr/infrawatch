import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Optional
from ..models.container import Alert, ContainerHealth, ContainerEvent

logger = logging.getLogger(__name__)


class AlertManager:
    """Manages alerts and notifications"""
    
    def __init__(self):
        self._active_alerts: dict[str, List[Alert]] = defaultdict(list)
        self._alert_history: List[Alert] = []
        self._max_history = 1000
        
        # Restart tracking
        self._restart_counts: dict[str, List[datetime]] = defaultdict(list)
        self._restart_window = 600  # 10 minutes
        self._restart_threshold = 5
    
    def add_alert(self, alert: Alert):
        """Add new alert"""
        # Check if similar alert already exists
        container_alerts = self._active_alerts[alert.container_id]
        
        # Don't duplicate if same alert type within last 60 seconds
        recent_similar = [
            a for a in container_alerts
            if a.alert_type == alert.alert_type
            and (alert.timestamp - a.timestamp).total_seconds() < 60
        ]
        
        if not recent_similar:
            self._active_alerts[alert.container_id].append(alert)
            self._alert_history.append(alert)
            
            # Trim history
            if len(self._alert_history) > self._max_history:
                self._alert_history = self._alert_history[-self._max_history:]
            
            logger.warning(f"Alert: {alert.message} ({alert.severity})")
    
    def get_active_alerts(self, container_id: Optional[str] = None) -> List[Alert]:
        """Get active alerts"""
        if container_id:
            return self._active_alerts.get(container_id, [])
        
        # Return all active alerts
        all_alerts = []
        for alerts in self._active_alerts.values():
            all_alerts.extend(alerts)
        return all_alerts
    
    def clear_alerts(self, container_id: str):
        """Clear alerts for container"""
        self._active_alerts[container_id] = []
    
    def check_health_alert(self, health: ContainerHealth) -> Optional[Alert]:
        """Check if health status requires alert"""
        if health.status == "unhealthy":
            return Alert(
                container_id=health.container_id,
                container_name=health.container_name,
                timestamp=health.timestamp,
                alert_type="health",
                severity="critical" if health.failing_streak >= 3 else "warning",
                message=f"Container unhealthy (failures: {health.failing_streak})",
                current_value=float(health.failing_streak),
                threshold=3.0
            )
        return None
    
    def track_restart(self, event: ContainerEvent) -> Optional[Alert]:
        """Track container restarts and generate alert if threshold exceeded"""
        if event.action not in ['restart', 'die', 'start']:
            return None
        
        # Add restart timestamp
        self._restart_counts[event.container_id].append(event.timestamp)
        
        # Clean old restarts outside window
        cutoff = datetime.utcnow() - timedelta(seconds=self._restart_window)
        self._restart_counts[event.container_id] = [
            ts for ts in self._restart_counts[event.container_id]
            if ts >= cutoff
        ]
        
        # Check threshold
        restart_count = len(self._restart_counts[event.container_id])
        if restart_count >= self._restart_threshold:
            return Alert(
                container_id=event.container_id,
                container_name=event.container_name,
                timestamp=event.timestamp,
                alert_type="restart",
                severity="critical",
                message=f"Container restarting frequently: {restart_count} times in {self._restart_window}s",
                current_value=float(restart_count),
                threshold=float(self._restart_threshold)
            )
        
        return None
