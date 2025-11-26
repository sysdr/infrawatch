import asyncio
from typing import Dict, Any
import structlog
from datetime import datetime
from app.core.metrics import MetricsCollector

logger = structlog.get_logger()

class AlertDispatcher:
    """Priority-based alert routing"""
    
    def __init__(self, metrics: MetricsCollector):
        self.metrics = metrics
        self.alert_queue = asyncio.Queue()
    
    async def dispatch_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch alert with priority"""
        start_time = datetime.now()
        
        try:
            severity = alert_data.get("severity", "info")
            priority_map = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
            priority = priority_map.get(severity, 4)
            
            alert = {
                "alert_id": f"alert_{datetime.now().timestamp()}",
                "severity": severity,
                "message": alert_data.get("message", ""),
                "created_at": datetime.now().isoformat(),
                "status": "active"
            }
            
            # Add to queue (priority handled by processing order if needed)
            # Using a tuple with a counter to ensure uniqueness for PriorityQueue-like behavior
            await self.alert_queue.put((priority, datetime.now().timestamp(), alert))
            
            latency = (datetime.now() - start_time).total_seconds() * 1000
            self.metrics.record_latency("alert_dispatch", latency)
            self.metrics.increment_counter(f"alerts_{severity}")
            self.metrics.increment_counter("alerts_created")
            
            return alert
            
        except Exception as e:
            logger.error("Alert dispatch failed", error=str(e))
            raise
