import asyncio
import time
from typing import Dict, List
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class AlertSeverity(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"

class AlertService:
    def __init__(self, stream_manager, metric_collector=None):
        self.stream_manager = stream_manager
        self.metric_collector = metric_collector
        self.running = False
        self.alert_history: List[Dict] = []
        self.thresholds = {
            'cpu_critical': 20.0,  # Lowered for demo purposes
            'cpu_warning': 10.0,   # Lowered for demo purposes
            'memory_critical': 30.0,  # Lowered for demo purposes
            'memory_warning': 15.0,   # Lowered for demo purposes
            'disk_critical': 90.0,
            'disk_warning': 70.0
        }
        self.alert_counts = {'critical': 0, 'warning': 0, 'info': 0}
        
    async def start_monitoring(self):
        """Start monitoring for alert conditions"""
        self.running = True
        logger.info("Alert service started")
        
        # Monitor metrics and check for alerts
        while self.running:
            try:
                if self.metric_collector and hasattr(self.metric_collector, 'last_metrics'):
                    metrics = self.metric_collector.last_metrics
                    if metrics:
                        alerts = await self.check_and_alert(metrics)
                        if alerts:
                            logger.info(f"Generated {len(alerts)} alert(s)")
                    else:
                        logger.debug("No metrics available yet")
            except Exception as e:
                logger.error(f"Error in alert monitoring: {e}")
            await asyncio.sleep(2)  # Check every 2 seconds
            
    async def check_and_alert(self, metrics: Dict):
        """Check metrics against thresholds and generate alerts"""
        alerts = []
        
        # Check CPU
        cpu_percent = metrics.get('cpu', {}).get('percent', 0)
        if cpu_percent >= self.thresholds['cpu_critical']:
            alerts.append(self._create_alert(
                AlertSeverity.CRITICAL,
                "CPU Usage Critical",
                f"CPU usage at {cpu_percent}%",
                {'metric': 'cpu', 'value': cpu_percent}
            ))
        elif cpu_percent >= self.thresholds['cpu_warning']:
            alerts.append(self._create_alert(
                AlertSeverity.WARNING,
                "CPU Usage High",
                f"CPU usage at {cpu_percent}%",
                {'metric': 'cpu', 'value': cpu_percent}
            ))
            
        # Check Memory
        mem_percent = metrics.get('memory', {}).get('percent', 0)
        if mem_percent >= self.thresholds['memory_critical']:
            alerts.append(self._create_alert(
                AlertSeverity.CRITICAL,
                "Memory Usage Critical",
                f"Memory usage at {mem_percent}%",
                {'metric': 'memory', 'value': mem_percent}
            ))
        elif mem_percent >= self.thresholds['memory_warning']:
            alerts.append(self._create_alert(
                AlertSeverity.WARNING,
                "Memory Usage High",
                f"Memory usage at {mem_percent}%",
                {'metric': 'memory', 'value': mem_percent}
            ))
            
        # Check Disk
        disk_percent = metrics.get('disk', {}).get('percent', 0)
        if disk_percent >= self.thresholds['disk_critical']:
            alerts.append(self._create_alert(
                AlertSeverity.CRITICAL,
                "Disk Usage Critical",
                f"Disk usage at {disk_percent}%",
                {'metric': 'disk', 'value': disk_percent}
            ))
        elif disk_percent >= self.thresholds['disk_warning']:
            alerts.append(self._create_alert(
                AlertSeverity.WARNING,
                "Disk Usage High",
                f"Disk usage at {disk_percent}%",
                {'metric': 'disk', 'value': disk_percent}
            ))
            
        # Broadcast alerts
        for alert in alerts:
            await self._broadcast_alert(alert)
            
        return alerts
        
    def _create_alert(self, severity: AlertSeverity, title: str, 
                     message: str, metadata: Dict) -> Dict:
        """Create alert object"""
        alert = {
            'id': f"alert_{int(time.time() * 1000)}",
            'severity': severity.value,
            'title': title,
            'message': message,
            'metadata': metadata,
            'timestamp': time.time(),
            'acknowledged': False
        }
        self.alert_history.append(alert)
        self.alert_counts[severity.value] += 1
        return alert
        
    async def _broadcast_alert(self, alert: Dict):
        """Broadcast alert to subscribers"""
        topic = f"alerts_{alert['severity']}"
        logger.info(f"Broadcasting alert to topic '{topic}': {alert['title']}")
        await self.stream_manager.broadcast(
            topic,
            alert,
            priority='critical'  # Alerts always critical priority
        )
        logger.warning(f"Alert broadcast: {alert['title']} - {alert['message']}")
        
    async def stop(self):
        self.running = False
        logger.info("Alert service stopped")
        
    def get_stats(self) -> Dict:
        return {
            'total_alerts': len(self.alert_history),
            'by_severity': self.alert_counts,
            'recent_alerts': self.alert_history[-10:]
        }
