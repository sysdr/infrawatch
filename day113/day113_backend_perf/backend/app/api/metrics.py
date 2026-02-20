import time
import psutil
from fastapi import APIRouter
from prometheus_client import REGISTRY, generate_latest
from app.services.cache import cache_service
from app.db.session import get_pool_stats
router = APIRouter(prefix="/metrics", tags=["metrics"])
def _parse_histogram(name: str) -> dict:
    output = generate_latest(REGISTRY).decode()
    total_count = 0
    total_sum = 0.0
    buckets = []
    for line in output.splitlines():
        if line.startswith(f"{name}_bucket"):
            parts = line.split()
            if len(parts) >= 2:
                le_val = None
                for token in parts[0].split(","):
                    if "le=" in token:
                        le_str = token.split("=")[1].strip('"{}')
                        try:
                            le_val = float(le_str)
                        except ValueError:
                            pass
                if le_val is not None:
                    try:
                        buckets.append((le_val, float(parts[1])))
                    except (IndexError, ValueError):
                        pass
        if line.startswith(f"{name}_count"):
            try:
                total_count = float(line.split()[-1])
            except (IndexError, ValueError):
                pass
        if line.startswith(f"{name}_sum"):
            try:
                total_sum = float(line.split()[-1])
            except (IndexError, ValueError):
                pass
    def percentile(p: float) -> float:
        if not buckets or total_count == 0:
            return 0.0
        target = p * total_count
        for le, count in sorted(buckets):
            if count >= target:
                return round(le * 1000, 1)
        return round(sorted(buckets)[-1][0] * 1000, 1)
    return {"p50_ms": percentile(0.50), "p95_ms": percentile(0.95), "p99_ms": percentile(0.99), "total_requests": int(total_count), "avg_ms": round((total_sum / total_count) * 1000, 1) if total_count > 0 else 0}
@router.get("/performance")
async def get_performance_metrics():
    latency = _parse_histogram("http_request_duration_seconds")
    pool_stats = await get_pool_stats()
    cache_stats = cache_service.stats
    cpu = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory()
    return {"latency": latency, "cache": cache_stats, "pool": pool_stats, "system": {"cpu_pct": cpu, "mem_used_pct": mem.percent, "mem_available_mb": round(mem.available / 1024 / 1024, 1)}, "timestamp": time.time()}
@router.get("/health/pool")
async def pool_health():
    stats = await get_pool_stats()
    healthy = stats["utilisation_pct"] < 80
    return {"healthy": healthy, **stats}
