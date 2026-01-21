import asyncio
import logging
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from ..models.container import ContainerMetrics, ContainerHealth, Alert

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collects and aggregates container metrics"""
    
    def __init__(self, window_size: int = 600):
        """
        Args:
            window_size: Size of sliding window in seconds (default: 10 minutes)
        """
        self.window_size = window_size
        
        # Store recent metrics for each container
        self._metrics_buffer: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=window_size)
        )
        
        # Store baselines
        self._baselines: Dict[str, Dict] = {}
        
        # Alert thresholds
        self.cpu_warning_threshold = 80.0
        self.cpu_critical_threshold = 95.0
        self.memory_warning_threshold = 80.0
        self.memory_critical_threshold = 95.0
        
    def add_metrics(self, metrics: ContainerMetrics):
        """Add metrics to buffer"""
        self._metrics_buffer[metrics.container_id].append(metrics)
        self._update_baseline(metrics.container_id)
    
    def get_latest_metrics(self, container_id: str) -> Optional[ContainerMetrics]:
        """Get latest metrics for container"""
        buffer = self._metrics_buffer.get(container_id)
        return buffer[-1] if buffer else None
    
    def get_metrics_history(
        self, container_id: str, duration_seconds: int = 60
    ) -> List[ContainerMetrics]:
        """Get metrics history for specified duration"""
        buffer = self._metrics_buffer.get(container_id, [])
        cutoff = datetime.utcnow() - timedelta(seconds=duration_seconds)
        return [m for m in buffer if m.timestamp >= cutoff]
    
    def get_baseline(self, container_id: str) -> Optional[Dict]:
        """Get baseline metrics for container"""
        return self._baselines.get(container_id)
    
    def check_anomalies(
        self, metrics: ContainerMetrics
    ) -> List[Alert]:
        """Check for anomalies in metrics"""
        alerts = []
        baseline = self._baselines.get(metrics.container_id)
        
        # CPU alerts
        if metrics.cpu_percent >= self.cpu_critical_threshold:
            alerts.append(Alert(
                container_id=metrics.container_id,
                container_name=metrics.container_name,
                timestamp=metrics.timestamp,
                alert_type="cpu",
                severity="critical",
                message=f"CPU usage critical: {metrics.cpu_percent:.1f}%",
                current_value=metrics.cpu_percent,
                threshold=self.cpu_critical_threshold,
                baseline=baseline['cpu_mean'] if baseline else None
            ))
        elif metrics.cpu_percent >= self.cpu_warning_threshold:
            alerts.append(Alert(
                container_id=metrics.container_id,
                container_name=metrics.container_name,
                timestamp=metrics.timestamp,
                alert_type="cpu",
                severity="warning",
                message=f"CPU usage high: {metrics.cpu_percent:.1f}%",
                current_value=metrics.cpu_percent,
                threshold=self.cpu_warning_threshold,
                baseline=baseline['cpu_mean'] if baseline else None
            ))
        
        # Memory alerts
        if metrics.memory_percent >= self.memory_critical_threshold:
            alerts.append(Alert(
                container_id=metrics.container_id,
                container_name=metrics.container_name,
                timestamp=metrics.timestamp,
                alert_type="memory",
                severity="critical",
                message=f"Memory usage critical: {metrics.memory_percent:.1f}%",
                current_value=metrics.memory_percent,
                threshold=self.memory_critical_threshold,
                baseline=baseline['memory_mean'] if baseline else None
            ))
        elif metrics.memory_percent >= self.memory_warning_threshold:
            alerts.append(Alert(
                container_id=metrics.container_id,
                container_name=metrics.container_name,
                timestamp=metrics.timestamp,
                alert_type="memory",
                severity="warning",
                message=f"Memory usage high: {metrics.memory_percent:.1f}%",
                current_value=metrics.memory_percent,
                threshold=self.memory_warning_threshold,
                baseline=baseline['memory_mean'] if baseline else None
            ))
        
        # Baseline anomaly detection
        if baseline:
            # CPU spike detection
            if metrics.cpu_percent > baseline['cpu_mean'] + 2 * baseline['cpu_stddev']:
                if metrics.cpu_percent < self.cpu_warning_threshold:  # Don't duplicate
                    alerts.append(Alert(
                        container_id=metrics.container_id,
                        container_name=metrics.container_name,
                        timestamp=metrics.timestamp,
                        alert_type="cpu",
                        severity="warning",
                        message=f"CPU spike detected: {metrics.cpu_percent:.1f}% "
                               f"(baseline: {baseline['cpu_mean']:.1f}%)",
                        current_value=metrics.cpu_percent,
                        threshold=baseline['cpu_mean'] + 2 * baseline['cpu_stddev'],
                        baseline=baseline['cpu_mean']
                    ))
            
            # Memory leak detection
            if metrics.memory_percent > baseline['memory_mean'] + 2 * baseline['memory_stddev']:
                if metrics.memory_percent < self.memory_warning_threshold:  # Don't duplicate
                    alerts.append(Alert(
                        container_id=metrics.container_id,
                        container_name=metrics.container_name,
                        timestamp=metrics.timestamp,
                        alert_type="memory",
                        severity="warning",
                        message=f"Memory anomaly detected: {metrics.memory_percent:.1f}% "
                               f"(baseline: {baseline['memory_mean']:.1f}%)",
                        current_value=metrics.memory_percent,
                        threshold=baseline['memory_mean'] + 2 * baseline['memory_stddev'],
                        baseline=baseline['memory_mean']
                    ))
        
        return alerts
    
    def _update_baseline(self, container_id: str):
        """Update baseline statistics for container"""
        buffer = self._metrics_buffer[container_id]
        
        if len(buffer) < 60:  # Need at least 1 minute of data
            return
        
        # Calculate statistics over last 10 minutes
        cpu_values = [m.cpu_percent for m in buffer]
        memory_values = [m.memory_percent for m in buffer]
        
        cpu_mean = sum(cpu_values) / len(cpu_values)
        memory_mean = sum(memory_values) / len(memory_values)
        
        # Calculate standard deviation
        cpu_variance = sum((x - cpu_mean) ** 2 for x in cpu_values) / len(cpu_values)
        memory_variance = sum((x - memory_mean) ** 2 for x in memory_values) / len(memory_values)
        
        cpu_stddev = cpu_variance ** 0.5
        memory_stddev = memory_variance ** 0.5
        
        self._baselines[container_id] = {
            'cpu_mean': cpu_mean,
            'cpu_stddev': cpu_stddev,
            'memory_mean': memory_mean,
            'memory_stddev': memory_stddev,
            'updated_at': datetime.utcnow()
        }
