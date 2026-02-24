import pytest, asyncio
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

@pytest.mark.asyncio
async def test_benchmark_runs():
    from app.services.benchmark import run_benchmark
    # Quick benchmark with very few iterations
    results = await run_benchmark("http://localhost:8117", iterations=5, concurrency=2)
    assert isinstance(results, list)
    assert len(results) > 0
    for r in results:
        assert "p50_ms" in r
        assert "p95_ms" in r
        assert "p99_ms" in r
        assert r["p50_ms"] >= 0

@pytest.mark.asyncio  
async def test_benchmark_result_fields():
    from app.services.benchmark import run_benchmark
    results = await run_benchmark("http://localhost:8117", iterations=3, concurrency=1)
    if results:
        r = results[0]
        assert "endpoint" in r
        assert "method" in r
        assert "throughput_rps" in r
        assert r["iterations"] == 3
