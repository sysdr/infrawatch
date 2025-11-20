import asyncio
import time
from dataclasses import dataclass
from typing import Dict, List
import psutil
import json
from .load_orchestrator import LoadTestOrchestrator, ping_scenario, mixed_scenario

@dataclass
class PerformanceReport:
    test_name: str
    connections: int
    duration_seconds: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    avg_latency_ms: float
    throughput_mps: float
    total_messages: int
    error_count: int
    error_rate: float
    connection_time_ms: float
    memory_usage_mb: float
    cpu_percent: float
    passed: bool
    
    def to_dict(self) -> Dict:
        return {
            "test_name": self.test_name,
            "connections": self.connections,
            "duration_seconds": self.duration_seconds,
            "latency": {
                "p50_ms": self.p50_latency_ms,
                "p95_ms": self.p95_latency_ms,
                "p99_ms": self.p99_latency_ms,
                "avg_ms": self.avg_latency_ms
            },
            "throughput_mps": self.throughput_mps,
            "total_messages": self.total_messages,
            "errors": {
                "count": self.error_count,
                "rate": self.error_rate
            },
            "resources": {
                "memory_mb": self.memory_usage_mb,
                "cpu_percent": self.cpu_percent
            },
            "passed": self.passed
        }

class PerformanceBenchmarker:
    def __init__(self, base_url: str = "ws://localhost:8000/ws"):
        self.base_url = base_url
        self.reports: List[PerformanceReport] = []
        
    async def run_benchmark(
        self,
        name: str,
        connections: int,
        duration: float,
        ramp_rate: int = 100,
        scenario_type: str = "mixed"
    ) -> PerformanceReport:
        """Run a single benchmark test"""
        orchestrator = LoadTestOrchestrator(self.base_url)
        
        # Select scenario
        scenario = mixed_scenario if scenario_type == "mixed" else ping_scenario
        
        # Record initial resources
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024
        
        # Spawn connections
        connect_start = time.time()
        await orchestrator.spawn_connections(connections, ramp_rate)
        connection_time = (time.time() - connect_start) * 1000
        
        # Run scenario
        await orchestrator.execute_scenario(scenario, duration)
        
        # Collect metrics
        metrics = orchestrator.collect_metrics()
        
        # Record final resources
        final_memory = process.memory_info().rss / 1024 / 1024
        cpu_percent = psutil.cpu_percent()
        
        # Cleanup
        await orchestrator.cleanup()
        
        # Create report
        report = PerformanceReport(
            test_name=name,
            connections=connections,
            duration_seconds=duration,
            p50_latency_ms=metrics.p50_latency,
            p95_latency_ms=metrics.p95_latency,
            p99_latency_ms=metrics.p99_latency,
            avg_latency_ms=sum(metrics.all_latencies) / len(metrics.all_latencies) if metrics.all_latencies else 0,
            throughput_mps=metrics.throughput_mps,
            total_messages=metrics.total_messages_sent,
            error_count=len(metrics.all_errors),
            error_rate=metrics.error_rate,
            connection_time_ms=connection_time,
            memory_usage_mb=final_memory - initial_memory,
            cpu_percent=cpu_percent,
            passed=metrics.p99_latency < 1000 and metrics.error_rate < 0.05
        )
        
        self.reports.append(report)
        return report
        
    async def run_standard_benchmarks(self) -> List[PerformanceReport]:
        """Run standard benchmark suite"""
        benchmarks = [
            ("small_load", 50, 30),
            ("medium_load", 200, 30),
            ("large_load", 500, 30),
            ("stress_test", 1000, 60)
        ]
        
        results = []
        for name, connections, duration in benchmarks:
            print(f"Running benchmark: {name} ({connections} connections, {duration}s)")
            report = await self.run_benchmark(name, connections, duration)
            results.append(report)
            print(f"  P99 Latency: {report.p99_latency_ms:.2f}ms, "
                  f"Throughput: {report.throughput_mps:.0f} msg/s, "
                  f"Passed: {report.passed}")
            
        return results
        
    def export_results(self, filepath: str):
        """Export results to JSON file"""
        data = {
            "benchmark_results": [r.to_dict() for r in self.reports],
            "timestamp": time.time()
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
