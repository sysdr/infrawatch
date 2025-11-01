"""
System reliability monitoring and health tracking
"""

import asyncio
import time
from collections import defaultdict, deque
from typing import Dict, List
import structlog

logger = structlog.get_logger()

class ReliabilityMonitor:
    """
    Monitors system reliability and provides health metrics
    """
    
    def __init__(self):
        self.metrics_window = 300  # 5 minutes
        self.delivery_results = defaultdict(lambda: deque(maxlen=1000))
        self.latency_samples = defaultdict(lambda: deque(maxlen=1000))
        self.error_counts = defaultdict(int)
        self.total_counts = defaultdict(int)
        self.running = False

    async def start(self):
        """Start reliability monitoring"""
        self.running = True
        logger.info("Reliability monitor started")

    async def stop(self):
        """Stop reliability monitoring"""
        self.running = False
        logger.info("Reliability monitor stopped")

    def record_delivery_attempt(self, channel: str, success: bool, latency_ms: float):
        """Record a delivery attempt result"""
        current_time = time.time()
        
        # Record result with timestamp
        self.delivery_results[channel].append({
            "timestamp": current_time,
            "success": success,
            "latency_ms": latency_ms
        })
        
        # Track latency
        self.latency_samples[channel].append(latency_ms)
        
        # Update counters
        self.total_counts[channel] += 1
        if not success:
            self.error_counts[channel] += 1

    async def get_system_health(self) -> Dict:
        """Calculate overall system health metrics"""
        current_time = time.time()
        cutoff_time = current_time - self.metrics_window
        
        channel_health = {}
        overall_success_rate = 0
        total_channels = 0
        total_attempts_all_channels = 0
        
        for channel in ["email", "sms", "push", "webhook"]:
            health = self._calculate_channel_health(channel, cutoff_time)
            channel_health[channel] = health
            total_attempts_all_channels += health["total_attempts"]
            
            if health["total_attempts"] > 0:
                overall_success_rate += health["success_rate"]
                total_channels += 1
        
        # Calculate overall health score
        # If no attempts have been made, default to 1.0 (healthy)
        # Otherwise, calculate average success rate
        if total_attempts_all_channels == 0:
            overall_health = 1.0  # System is healthy when no activity (no failures)
        else:
            overall_health = overall_success_rate / max(total_channels, 1)
        
        return {
            "overall_health": overall_health,
            "channels": channel_health,
            "timestamp": current_time,
            "window_minutes": self.metrics_window / 60
        }

    def _calculate_channel_health(self, channel: str, cutoff_time: float) -> Dict:
        """Calculate health metrics for a specific channel"""
        recent_results = [
            result for result in self.delivery_results[channel]
            if result["timestamp"] >= cutoff_time
        ]
        
        if not recent_results:
            return {
                "success_rate": 1.0,
                "total_attempts": 0,
                "avg_latency_ms": 0,
                "p95_latency_ms": 0,
                "error_rate": 0
            }
        
        # Calculate success rate
        successful = sum(1 for r in recent_results if r["success"])
        total = len(recent_results)
        success_rate = successful / total if total > 0 else 0
        
        # Calculate latency metrics
        latencies = [r["latency_ms"] for r in recent_results]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        
        # Calculate p95 latency
        sorted_latencies = sorted(latencies) if latencies else []
        p95_index = int(0.95 * len(sorted_latencies))
        p95_latency = sorted_latencies[p95_index] if sorted_latencies else 0
        
        return {
            "success_rate": success_rate,
            "total_attempts": total,
            "successful_attempts": successful,
            "avg_latency_ms": avg_latency,
            "p95_latency_ms": p95_latency,
            "error_rate": 1 - success_rate
        }

    async def get_circuit_breaker_status(self) -> Dict:
        """Get circuit breaker status for all channels"""
        # This would integrate with actual circuit breakers
        status = {}
        
        for channel in ["email", "sms", "push", "webhook"]:
            recent_errors = self.error_counts.get(channel, 0)
            recent_total = self.total_counts.get(channel, 0)
            
            error_rate = recent_errors / max(recent_total, 1)
            
            status[channel] = {
                "state": "open" if error_rate > 0.5 else "closed",
                "error_rate": error_rate,
                "recent_errors": recent_errors,
                "recent_total": recent_total
            }
        
        return status

    def get_reliability_summary(self) -> Dict:
        """Get summary of reliability metrics"""
        summary = {
            "total_channels": len(self.delivery_results),
            "channels": {},
            "overall_metrics": {
                "total_attempts": sum(self.total_counts.values()),
                "total_errors": sum(self.error_counts.values())
            }
        }
        
        for channel, results in self.delivery_results.items():
            if results:
                recent_results = list(results)[-100:]  # Last 100 attempts
                successful = sum(1 for r in recent_results if r["success"])
                
                summary["channels"][channel] = {
                    "recent_attempts": len(recent_results),
                    "recent_success_rate": successful / len(recent_results),
                    "total_attempts": self.total_counts[channel],
                    "total_errors": self.error_counts[channel]
                }
        
        return summary
