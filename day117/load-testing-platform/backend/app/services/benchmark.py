import asyncio, time, aiohttp, numpy as np
from typing import List, Dict, Any

ENDPOINTS = [
    ("GET", "/api/health"),
    ("GET", "/api/users?page=1&limit=20"),
    ("GET", "/api/users/1"),
    ("GET", "/api/teams"),
    ("GET", "/api/teams/1"),
    ("GET", "/api/dashboard/stats"),
]

async def _timed_request(session: aiohttp.ClientSession, method: str, url: str) -> float:
    t0 = time.perf_counter()
    try:
        async with session.request(method, url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            await resp.read()
            return (time.perf_counter() - t0) * 1000  # ms
    except Exception:
        return -1.0

async def run_benchmark(base_url: str, iterations: int = 200, concurrency: int = 10) -> List[Dict[str, Any]]:
    results = []
    connector = aiohttp.TCPConnector(limit=concurrency + 5)
    async with aiohttp.ClientSession(connector=connector) as session:
        for method, path in ENDPOINTS:
            url = base_url.rstrip("/") + path
            latencies: List[float] = []
            errors = 0
            t_start = time.perf_counter()

            for batch_start in range(0, iterations, concurrency):
                batch_size = min(concurrency, iterations - batch_start)
                tasks = [_timed_request(session, method, url) for _ in range(batch_size)]
                batch_results = await asyncio.gather(*tasks)
                for r in batch_results:
                    if r < 0:
                        errors += 1
                    else:
                        latencies.append(r)

            total_time = time.perf_counter() - t_start
            if latencies:
                results.append({
                    "endpoint": path,
                    "method": method,
                    "p50_ms": round(float(np.percentile(latencies, 50)), 2),
                    "p95_ms": round(float(np.percentile(latencies, 95)), 2),
                    "p99_ms": round(float(np.percentile(latencies, 99)), 2),
                    "mean_ms": round(float(np.mean(latencies)), 2),
                    "throughput_rps": round(len(latencies) / max(total_time, 0.001), 2),
                    "error_count": errors,
                    "iterations": iterations,
                })
    return results
