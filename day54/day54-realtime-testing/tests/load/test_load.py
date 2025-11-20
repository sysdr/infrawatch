import pytest
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))
from app.testing.load_orchestrator import (
    LoadTestOrchestrator, 
    ping_scenario, 
    mixed_scenario
)
from app.testing.benchmarker import PerformanceBenchmarker

BASE_URL = "ws://localhost:8000/ws"

class TestLoadScenarios:
    @pytest.mark.asyncio
    async def test_small_load(self):
        orchestrator = LoadTestOrchestrator(BASE_URL)
        
        # Spawn 50 connections
        await orchestrator.spawn_connections(50, ramp_rate=50)
        
        # Run for 10 seconds
        await orchestrator.execute_scenario(ping_scenario, 10)
        
        metrics = orchestrator.collect_metrics()
        await orchestrator.cleanup()
        
        assert metrics.successful_connections >= 45  # 90% success
        assert metrics.p99_latency < 500  # Under 500ms
        
    @pytest.mark.asyncio
    async def test_medium_load(self):
        orchestrator = LoadTestOrchestrator(BASE_URL)
        
        await orchestrator.spawn_connections(100, ramp_rate=50)
        await orchestrator.execute_scenario(mixed_scenario, 15)
        
        metrics = orchestrator.collect_metrics()
        await orchestrator.cleanup()
        
        assert metrics.connection_success_rate > 0.9
        assert metrics.throughput_mps > 0
        
    @pytest.mark.asyncio
    async def test_ramp_up(self):
        orchestrator = LoadTestOrchestrator(BASE_URL)
        
        # Slow ramp to test gradual load
        await orchestrator.spawn_connections(200, ramp_rate=20)
        await orchestrator.execute_scenario(ping_scenario, 20)
        
        metrics = orchestrator.collect_metrics()
        await orchestrator.cleanup()
        
        assert metrics.successful_connections >= 180

class TestBenchmarks:
    @pytest.mark.asyncio
    async def test_benchmark_suite(self):
        benchmarker = PerformanceBenchmarker(BASE_URL)
        
        # Run small benchmark
        report = await benchmarker.run_benchmark(
            "quick_test",
            connections=30,
            duration=10
        )
        
        assert report.total_messages > 0
        assert report.throughput_mps > 0
