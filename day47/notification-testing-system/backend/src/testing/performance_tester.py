"""
Performance testing for notification system under various load patterns
"""

import asyncio
import time
from typing import Dict, List, Callable
import random
from concurrent.futures import ThreadPoolExecutor
import structlog
from core.notification_service import NotificationService

logger = structlog.get_logger()

class PerformanceTester:
    """
    Conducts performance tests with different load patterns
    """
    
    def __init__(self):
        self.notification_service = NotificationService()
        self.test_data_generators = {
            "burst": self._generate_burst_load,
            "sustained": self._generate_sustained_load,
            "mixed": self._generate_mixed_load,
            "ramp": self._generate_ramp_load
        }

    async def run_performance_test(self, config: Dict) -> Dict:
        """
        Run performance test with specified configuration
        """
        test_type = config.get("type", "sustained")
        duration = config.get("duration_seconds", 60)
        target_rps = config.get("target_rps", 10)
        
        logger.info(f"Starting performance test", 
                   type=test_type, duration=duration, target_rps=target_rps)
        
        test_start = time.time()
        results = {
            "config": config,
            "start_time": test_start,
            "metrics": [],
            "summary": {}
        }
        
        # Generate test load
        if test_type in self.test_data_generators:
            generator = self.test_data_generators[test_type]
            metrics = await generator(target_rps, duration)
            results["metrics"] = metrics
        else:
            raise ValueError(f"Unknown test type: {test_type}")
        
        # Calculate summary statistics
        results["end_time"] = time.time()
        results["actual_duration"] = results["end_time"] - test_start
        results["summary"] = self._calculate_performance_summary(metrics)
        
        logger.info("Performance test completed", summary=results["summary"])
        return results

    async def _generate_burst_load(self, target_rps: int, duration: int) -> List[Dict]:
        """Generate burst load pattern - sudden spikes"""
        metrics = []
        end_time = time.time() + duration
        
        while time.time() < end_time:
            # Burst period: high load for 5 seconds
            burst_start = time.time()
            burst_metrics = await self._execute_load_burst(target_rps * 3, 5)
            metrics.extend(burst_metrics)
            
            # Quiet period: low load for 10 seconds
            if time.time() < end_time:
                quiet_metrics = await self._execute_load_burst(target_rps // 3, 10)
                metrics.extend(quiet_metrics)
        
        return metrics

    async def _generate_sustained_load(self, target_rps: int, duration: int) -> List[Dict]:
        """Generate sustained constant load"""
        return await self._execute_load_burst(target_rps, duration)

    async def _generate_mixed_load(self, target_rps: int, duration: int) -> List[Dict]:
        """Generate mixed workload with different priorities and channels"""
        metrics = []
        end_time = time.time() + duration
        
        channels = ["email", "sms", "push", "webhook"]
        priorities = ["low", "normal", "high", "urgent"]
        
        # Calculate request interval
        interval = 1.0 / target_rps
        
        request_count = 0
        while time.time() < end_time:
            batch_start = time.time()
            
            # Create batch of requests with mixed characteristics
            batch_size = min(10, target_rps // 4)  # Process in small batches
            batch_tasks = []
            
            for _ in range(batch_size):
                notification_data = {
                    "user_id": f"perf_test_{request_count}",
                    "channel": random.choice(channels),
                    "content": f"Performance test notification {request_count}",
                    "priority": random.choice(priorities)
                }
                
                task = self._send_and_measure(notification_data, request_count)
                batch_tasks.append(task)
                request_count += 1
            
            # Execute batch concurrently
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            for result in batch_results:
                if not isinstance(result, Exception):
                    metrics.append(result)
            
            # Maintain target rate
            batch_duration = time.time() - batch_start
            target_batch_duration = batch_size * interval
            
            if batch_duration < target_batch_duration:
                await asyncio.sleep(target_batch_duration - batch_duration)
        
        return metrics

    async def _generate_ramp_load(self, target_rps: int, duration: int) -> List[Dict]:
        """Generate ramping load pattern - gradually increasing"""
        metrics = []
        end_time = time.time() + duration
        
        ramp_duration = duration // 3  # Ramp up over 1/3 of test duration
        
        while time.time() < end_time:
            elapsed = time.time() - (end_time - duration)
            
            if elapsed < ramp_duration:
                # Ramp up phase
                current_rps = int(target_rps * (elapsed / ramp_duration))
            elif elapsed < duration - ramp_duration:
                # Sustained phase
                current_rps = target_rps
            else:
                # Ramp down phase
                remaining = end_time - time.time()
                current_rps = int(target_rps * (remaining / ramp_duration))
            
            if current_rps > 0:
                batch_metrics = await self._execute_load_burst(current_rps, 5)
                metrics.extend(batch_metrics)
            else:
                await asyncio.sleep(1)
        
        return metrics

    async def _execute_load_burst(self, rps: int, duration: int) -> List[Dict]:
        """Execute a burst of requests at specified RPS"""
        metrics = []
        
        if rps <= 0:
            return metrics
            
        interval = 1.0 / rps
        end_time = time.time() + duration
        request_count = 0
        
        while time.time() < end_time:
            batch_start = time.time()
            
            # Send notification and measure
            notification_data = {
                "user_id": f"burst_test_{request_count}",
                "channel": random.choice(["email", "sms", "push"]),
                "content": f"Burst test notification {request_count}",
                "priority": "normal"
            }
            
            try:
                metric = await self._send_and_measure(notification_data, request_count)
                metrics.append(metric)
            except Exception as e:
                logger.error(f"Request failed during burst test: {e}")
            
            request_count += 1
            
            # Rate limiting
            elapsed = time.time() - batch_start
            if elapsed < interval:
                await asyncio.sleep(interval - elapsed)
        
        return metrics

    async def _send_and_measure(self, notification_data: Dict, request_id: int) -> Dict:
        """Send notification and measure performance"""
        start_time = time.time()
        
        try:
            result = await self.notification_service.send_notification(notification_data)
            
            return {
                "request_id": request_id,
                "timestamp": start_time,
                "channel": notification_data["channel"],
                "success": result["success"],
                "latency_ms": result.get("latency_ms", 0),
                "total_time_ms": (time.time() - start_time) * 1000,
                "attempts": result.get("attempts", 1),
                "error": result.get("error")
            }
        except Exception as e:
            return {
                "request_id": request_id,
                "timestamp": start_time,
                "channel": notification_data["channel"],
                "success": False,
                "latency_ms": 0,
                "total_time_ms": (time.time() - start_time) * 1000,
                "attempts": 0,
                "error": str(e)
            }

    def _calculate_performance_summary(self, metrics: List[Dict]) -> Dict:
        """Calculate performance summary statistics"""
        if not metrics:
            return {"error": "No metrics collected"}
        
        total_requests = len(metrics)
        successful_requests = sum(1 for m in metrics if m["success"])
        
        # Calculate latency statistics
        latencies = [m["latency_ms"] for m in metrics if m["success"]]
        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            sorted_latencies = sorted(latencies)
            p50_latency = sorted_latencies[len(sorted_latencies) // 2]
            p95_latency = sorted_latencies[int(len(sorted_latencies) * 0.95)]
            p99_latency = sorted_latencies[int(len(sorted_latencies) * 0.99)]
        else:
            avg_latency = p50_latency = p95_latency = p99_latency = 0
        
        # Calculate throughput
        if metrics:
            duration = max(m["timestamp"] for m in metrics) - min(m["timestamp"] for m in metrics)
            throughput = total_requests / max(duration, 1)
        else:
            throughput = 0
        
        # Per-channel statistics
        by_channel = {}
        for metric in metrics:
            channel = metric["channel"]
            if channel not in by_channel:
                by_channel[channel] = {"total": 0, "successful": 0, "latencies": []}
            
            by_channel[channel]["total"] += 1
            if metric["success"]:
                by_channel[channel]["successful"] += 1
                by_channel[channel]["latencies"].append(metric["latency_ms"])
        
        # Calculate per-channel averages
        for channel, stats in by_channel.items():
            if stats["latencies"]:
                stats["avg_latency_ms"] = sum(stats["latencies"]) / len(stats["latencies"])
                stats["success_rate"] = stats["successful"] / stats["total"]
            else:
                stats["avg_latency_ms"] = 0
                stats["success_rate"] = 0
            del stats["latencies"]  # Remove raw data from summary
        
        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "success_rate": successful_requests / total_requests,
            "avg_latency_ms": avg_latency,
            "p50_latency_ms": p50_latency,
            "p95_latency_ms": p95_latency,
            "p99_latency_ms": p99_latency,
            "throughput_rps": throughput,
            "by_channel": by_channel
        }
