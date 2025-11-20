#!/usr/bin/env python3
"""
Complete test suite runner for WebSocket testing
"""
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '.')
from app.testing.load_orchestrator import LoadTestOrchestrator, mixed_scenario
from app.testing.benchmarker import PerformanceBenchmarker
from app.testing.concurrency_tests import ConcurrencyTestSuite
from app.testing.chaos_tests import ChaosTestSuite

BASE_URL = "ws://localhost:8000/ws"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = PROJECT_ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

async def run_full_test_suite():
    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": []
    }
    
    print("=" * 60)
    print("WebSocket Testing Suite - Full Run")
    print("=" * 60)
    
    # Concurrency Tests
    print("\n[1/3] Running Concurrency Tests...")
    concurrency_suite = ConcurrencyTestSuite(BASE_URL)
    concurrency_results = await concurrency_suite.run_all_tests()
    
    for result in concurrency_results:
        status = "✓ PASS" if result["passed"] else "✗ FAIL"
        print(f"  {status} - {result['test']}")
        results["tests"].append(result)
    
    # Give server time to recover from previous tests
    print("\nWaiting for server to recover...")
    await asyncio.sleep(2)
        
    # Chaos Tests
    print("\n[2/3] Running Chaos Tests...")
    chaos_suite = ChaosTestSuite(BASE_URL)
    chaos_results = await chaos_suite.run_all_tests()
    
    for result in chaos_results:
        status = "✓ PASS" if result["passed"] else "✗ FAIL"
        print(f"  {status} - {result['test']}")
        results["tests"].append(result)
    
    # Give server time to recover from previous tests
    print("\nWaiting for server to recover...")
    await asyncio.sleep(2)
        
    # Performance Benchmarks
    print("\n[3/3] Running Performance Benchmarks...")
    benchmarker = PerformanceBenchmarker(BASE_URL)
    
    # Quick benchmark for demo
    report = await benchmarker.run_benchmark(
        "demo_benchmark",
        connections=10,
        duration=5
    )
    
    benchmark_result = {
        "test": "performance_benchmark",
        "passed": report.passed,
        "p99_latency_ms": report.p99_latency_ms,
        "throughput_mps": report.throughput_mps,
        "error_rate": report.error_rate
    }
    results["tests"].append(benchmark_result)
    
    status = "✓ PASS" if report.passed else "✗ FAIL"
    print(f"  {status} - Performance Benchmark")
    print(f"    P99 Latency: {report.p99_latency_ms:.2f}ms")
    print(f"    Throughput: {report.throughput_mps:.0f} msg/s")
    
    # Summary
    print("\n" + "=" * 60)
    total = len(results["tests"])
    passed = sum(1 for t in results["tests"] if t["passed"])
    failed = total - passed
    
    print(f"Results: {passed}/{total} tests passed")
    if failed > 0:
        print(f"  ✗ {failed} tests failed")
    else:
        print("  ✓ All tests passed!")
        
    # Save results
    results_path = REPORTS_DIR / "test_results.json"
    with results_path.open("w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {results_path}")
    
    return failed == 0

if __name__ == "__main__":
    success = asyncio.run(run_full_test_suite())
    sys.exit(0 if success else 1)
