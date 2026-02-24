import asyncio, subprocess, time, uuid, json, sys, os
from datetime import datetime
from typing import Dict, Any, Optional, Callable
import aiohttp
import numpy as np
import psutil

# In-memory run state
_runs: Dict[str, Dict[str, Any]] = {}
_metric_callbacks: Dict[str, list] = {}

def get_run(run_id: str) -> Optional[Dict[str, Any]]:
    return _runs.get(run_id)

def get_all_runs() -> list:
    return sorted(_runs.values(), key=lambda r: r.get("created_at", ""), reverse=True)

def register_metric_callback(run_id: str, callback: Callable):
    if run_id not in _metric_callbacks:
        _metric_callbacks[run_id] = []
    _metric_callbacks[run_id].append(callback)

def unregister_metric_callback(run_id: str, callback: Callable):
    if run_id in _metric_callbacks:
        _metric_callbacks[run_id] = [c for c in _metric_callbacks[run_id] if c != callback]

async def _broadcast_metric(run_id: str, data: Dict):
    for cb in _metric_callbacks.get(run_id, []):
        try:
            await cb(data)
        except Exception:
            pass

async def _simulate_load_test(run_id: str, config: Dict[str, Any]):
    """
    Simulates a realistic load test by firing actual HTTP requests
    to the target API with configurable concurrency and duration.
    """
    run = _runs[run_id]
    run["status"] = "warming_up"
    run["started_at"] = datetime.utcnow().isoformat()

    base_url = config.get("target_url", "http://localhost:8117")
    max_users = config.get("users", 10)
    duration = config.get("duration_seconds", 30)
    test_type = config.get("test_type", "load")

    endpoints = [
        "/api/health",
        "/api/users?page=1&limit=20",
        "/api/users/1",
        "/api/teams",
        "/api/teams/1",
        "/api/dashboard/stats",
    ]

    total_requests = 0
    total_failures = 0
    all_latencies = []
    phase_latencies = []

    connector = aiohttp.TCPConnector(limit=max_users + 10)

    async def fire_request(session, endpoint, user_idx):
        import random
        t0 = time.perf_counter()
        try:
            url = base_url.rstrip("/") + endpoint
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                await resp.read()
                lat = (time.perf_counter() - t0) * 1000
                return lat, resp.status >= 400
        except Exception:
            return (time.perf_counter() - t0) * 1000, True

    import random

    async with aiohttp.ClientSession(connector=connector) as session:
        start_time = time.time()
        elapsed = 0

        # Phases: warm(5s), ramp(10s), sustained(rest), spike(5s if time allows)
        warm_duration = min(5, duration // 6)
        ramp_duration = min(10, duration // 3)
        sustained_duration = duration - warm_duration - ramp_duration - 5
        spike_duration = 5

        phase = "warm"
        phase_start = start_time
        current_users = max(1, max_users // 5)

        while elapsed < duration:
            elapsed = time.time() - start_time

            # Determine phase
            if elapsed < warm_duration:
                phase = "warming_up"
                current_users = max(1, max_users // 5)
            elif elapsed < warm_duration + ramp_duration:
                phase = "ramping"
                ramp_progress = (elapsed - warm_duration) / ramp_duration
                current_users = int(max(1, max_users // 5) + ramp_progress * (max_users - max_users // 5))
            elif elapsed < duration - spike_duration:
                phase = "sustained"
                current_users = max_users
            else:
                phase = "spike"
                current_users = min(max_users * 3, 50)

            run["status"] = "running"
            run["phase"] = phase

            # Fire a batch
            batch_endpoints = random.choices(endpoints, weights=[3, 2, 2, 2, 1, 1], k=current_users)
            tasks = [fire_request(session, ep, i) for i, ep in enumerate(batch_endpoints)]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            batch_latencies = []
            batch_failures = 0
            for r in results:
                if isinstance(r, Exception):
                    batch_failures += 1
                    total_failures += 1
                else:
                    lat, failed = r
                    if failed:
                        batch_failures += 1
                        total_failures += 1
                    else:
                        batch_latencies.append(lat)
                        total_requests += 1
                        all_latencies.append(lat)
                        phase_latencies.append(lat)

            # Compute snapshot metrics
            elapsed_since_last = 0.1
            rps = len(batch_latencies) / max(elapsed_since_last, 0.001)

            if phase_latencies:
                p50 = float(np.percentile(phase_latencies[-200:], 50))
                p95 = float(np.percentile(phase_latencies[-200:], 95))
                p99 = float(np.percentile(phase_latencies[-200:], 99))
            else:
                p50 = p95 = p99 = 0

            total = total_requests + total_failures
            err_rate = (total_failures / max(total, 1)) * 100

            sys_metrics = {}
            try:
                sys_metrics = {
                    "cpu_percent": psutil.cpu_percent(interval=None),
                    "memory_percent": psutil.virtual_memory().percent,
                }
            except Exception:
                sys_metrics = {"cpu_percent": 0, "memory_percent": 0}

            metric = {
                "type": "metric",
                "run_id": run_id,
                "timestamp": time.time(),
                "elapsed_seconds": round(elapsed, 1),
                "phase": phase,
                "rps": round(rps * current_users, 1),
                "p50_ms": round(p50, 2),
                "p95_ms": round(p95, 2),
                "p99_ms": round(p99, 2),
                "error_rate": round(err_rate, 2),
                "active_users": current_users,
                "total_requests": total_requests,
                "failed_requests": total_failures,
                **sys_metrics
            }
            run["latest_metric"] = metric
            await _broadcast_metric(run_id, metric)
            await asyncio.sleep(0.5)

    # Finalize
    run["status"] = "completed"
    run["finished_at"] = datetime.utcnow().isoformat()

    if all_latencies:
        run["summary"] = {
            "p50_ms": round(float(np.percentile(all_latencies, 50)), 2),
            "p95_ms": round(float(np.percentile(all_latencies, 95)), 2),
            "p99_ms": round(float(np.percentile(all_latencies, 99)), 2),
            "mean_ms": round(float(np.mean(all_latencies)), 2),
            "total_requests": total_requests,
            "total_failures": total_failures,
            "error_rate_percent": round((total_failures / max(total_requests + total_failures, 1)) * 100, 2),
        }
    else:
        run["summary"] = {}

    await _broadcast_metric(run_id, {"type": "completed", "run_id": run_id, **run.get("summary", {})})


async def _run_stress_test(run_id: str, config: Dict[str, Any]):
    """Binary search stress test to find max sustainable RPS."""
    run = _runs[run_id]
    run["status"] = "stress_binary_search"
    base_url = config.get("target_url", "http://localhost:8117")
    error_threshold = config.get("error_threshold_percent", 5.0)

    lo, hi = 5, 200
    last_good_rps = 0
    breakdown_rps = hi

    connector = aiohttp.TCPConnector(limit=50)

    async def measure_at_rps(target_rps: float) -> float:
        """Returns error rate at given RPS for 5s sample."""
        requests_per_second = int(target_rps)
        errors = 0
        total = 0
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=requests_per_second + 5)) as sess:
            for _ in range(3):  # 3 second sample
                tasks = [sess.get(
                    base_url.rstrip("/") + "/api/users?page=1&limit=20",
                    timeout=aiohttp.ClientTimeout(total=3)
                ) for _ in range(requests_per_second)]
                for coro in asyncio.as_completed(tasks):
                    try:
                        async with await coro as resp:
                            await resp.read()
                            if resp.status >= 500:
                                errors += 1
                            total += 1
                    except Exception:
                        errors += 1
                        total += 1
                await asyncio.sleep(1)
        return (errors / max(total, 1)) * 100

    # Binary search
    iterations = 0
    while lo <= hi and iterations < 8:
        mid = (lo + hi) / 2
        err_rate = await measure_at_rps(mid)

        metric = {
            "type": "stress_probe",
            "run_id": run_id,
            "probed_rps": mid,
            "error_rate": round(err_rate, 2),
            "phase": "binary_search",
            "timestamp": time.time(),
        }
        run["latest_metric"] = metric
        await _broadcast_metric(run_id, metric)

        if err_rate < error_threshold:
            last_good_rps = mid
            lo = mid + 1
        else:
            breakdown_rps = mid
            hi = mid - 1
        iterations += 1

    sys_metrics = {"cpu_percent": psutil.cpu_percent(), "memory_percent": psutil.virtual_memory().percent}

    run["status"] = "completed"
    run["finished_at"] = datetime.utcnow().isoformat()
    run["summary"] = {
        "max_rps_sustainable": round(last_good_rps, 1),
        "breakdown_rps": round(breakdown_rps, 1),
        "error_threshold_percent": error_threshold,
        "breakdown_cpu": sys_metrics["cpu_percent"],
        "breakdown_memory": sys_metrics["memory_percent"],
    }

    await _broadcast_metric(run_id, {"type": "stress_completed", "run_id": run_id, **run["summary"]})
    await connector.close()


async def start_test_run(config: Dict[str, Any]) -> str:
    run_id = str(uuid.uuid4())
    test_type = config.get("test_type", "load")
    run = {
        "id": run_id,
        "name": config.get("name", f"Run-{run_id[:8]}"),
        "status": "queued",
        "test_type": test_type,
        "config": config,
        "created_at": datetime.utcnow().isoformat(),
        "started_at": None,
        "finished_at": None,
        "phase": "idle",
        "latest_metric": {},
        "summary": {},
    }
    _runs[run_id] = run

    if test_type == "stress":
        asyncio.create_task(_run_stress_test(run_id, config))
    elif test_type == "benchmark":
        asyncio.create_task(_run_benchmark_task(run_id, config))
    else:
        asyncio.create_task(_simulate_load_test(run_id, config))

    return run_id


async def _run_benchmark_task(run_id: str, config: Dict[str, Any]):
    from app.services.benchmark import run_benchmark
    run = _runs[run_id]
    run["status"] = "running"
    run["started_at"] = datetime.utcnow().isoformat()
    base_url = config.get("target_url", "http://localhost:8117")
    await _broadcast_metric(run_id, {"type": "benchmark_started", "run_id": run_id})
    results = await run_benchmark(base_url, iterations=100, concurrency=8)
    run["status"] = "completed"
    run["finished_at"] = datetime.utcnow().isoformat()
    run["summary"] = {"benchmarks": results}
    await _broadcast_metric(run_id, {"type": "benchmark_completed", "run_id": run_id, "benchmarks": results})
