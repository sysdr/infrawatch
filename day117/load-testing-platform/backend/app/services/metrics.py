import psutil, time, asyncio
from typing import Dict, Any

def collect_system_metrics() -> Dict[str, Any]:
    cpu = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory()
    net = psutil.net_io_counters()
    try:
        connections = len(psutil.net_connections(kind='inet'))
    except (psutil.AccessDenied, PermissionError):
        connections = 0
    return {
        "cpu_percent": round(cpu, 1),
        "memory_percent": round(mem.percent, 1),
        "memory_used_mb": round(mem.used / 1024 / 1024, 1),
        "memory_total_mb": round(mem.total / 1024 / 1024, 1),
        "net_connections": connections,
        "bytes_sent_mb": round(net.bytes_sent / 1024 / 1024, 2),
        "bytes_recv_mb": round(net.bytes_recv / 1024 / 1024, 2),
        "timestamp": time.time(),
    }

class MetricsSampler:
    """Continuously samples system metrics in background."""
    def __init__(self, interval: float = 2.0):
        self.interval = interval
        self.latest: Dict[str, Any] = {}
        self._task = None

    async def start(self):
        self._task = asyncio.create_task(self._loop())

    async def _loop(self):
        while True:
            self.latest = collect_system_metrics()
            await asyncio.sleep(self.interval)

    async def stop(self):
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

metrics_sampler = MetricsSampler()
