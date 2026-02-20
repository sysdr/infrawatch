import json
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
import numpy as np
from app.models.analytics import MetricSnapshot
from app.schemas.analytics import DashboardKPI, DashboardResponse
import redis.asyncio as aioredis

METRIC_NAMES = ["cpu_utilization", "memory_usage", "request_latency_ms",
                "error_rate", "throughput_rps", "queue_depth",
                "disk_io_mbps", "network_out_mbps"]

class AnalyticsService:
    def __init__(self, db: AsyncSession, redis: aioredis.Redis):
        self.db = db
        self.redis = redis

    async def seed_metrics(self):
        """Seed realistic metric data if table is empty."""
        result = await self.db.execute(select(func.count()).select_from(MetricSnapshot))
        count = result.scalar()
        if count and count > 0:
            return

        now = datetime.now(timezone.utc)
        snapshots = []
        for i in range(720):  # 12 hours of data at 1-min intervals
            ts = now - timedelta(minutes=720 - i)
            base_values = {
                "cpu_utilization": 45 + 20 * np.sin(i * 0.05) + np.random.normal(0, 3),
                "memory_usage": 62 + 8 * np.sin(i * 0.03) + np.random.normal(0, 2),
                "request_latency_ms": 120 + 60 * abs(np.sin(i * 0.08)) + np.random.normal(0, 10),
                "error_rate": max(0, 0.5 + 0.3 * np.sin(i * 0.1) + np.random.normal(0, 0.1)),
                "throughput_rps": 850 + 200 * np.sin(i * 0.04) + np.random.normal(0, 30),
                "queue_depth": max(0, 15 + 10 * np.sin(i * 0.07) + np.random.normal(0, 3)),
                "disk_io_mbps": 45 + 15 * np.sin(i * 0.06) + np.random.normal(0, 5),
                "network_out_mbps": 120 + 40 * np.sin(i * 0.05) + np.random.normal(0, 8),
            }
            for name, val in base_values.items():
                snapshots.append(MetricSnapshot(metric_name=name, value=round(float(val), 2),
                                                unit="", tags={"env": "prod"}, recorded_at=ts))

        self.db.add_all(snapshots)
        await self.db.commit()

    async def get_dashboard(self) -> DashboardResponse:
        cache_key = "dashboard:kpis"
        cached = await self.redis.get(cache_key)
        if cached:
            data = json.loads(cached)
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
            data["kpis"] = [DashboardKPI(**k) for k in data["kpis"]]
            return DashboardResponse(**data)

        now = datetime.now(timezone.utc)
        window_1h = now - timedelta(hours=1)
        window_2h = now - timedelta(hours=2)

        kpis = []
        for metric in METRIC_NAMES:
            # Current window: avg and ordered values for sparkline (separate to avoid GROUP BY issue)
            r = await self.db.execute(
                select(func.avg(MetricSnapshot.value))
                .where(MetricSnapshot.metric_name == metric, MetricSnapshot.recorded_at >= window_1h)
            )
            current_avg = float(r.scalar() or 0)
            r_values = await self.db.execute(
                select(MetricSnapshot.value)
                .where(MetricSnapshot.metric_name == metric, MetricSnapshot.recorded_at >= window_1h)
                .order_by(MetricSnapshot.recorded_at)
            )
            values_list = [row[0] for row in r_values.fetchall()]

            # Previous window for trend
            r2 = await self.db.execute(
                select(func.avg(MetricSnapshot.value))
                .where(MetricSnapshot.metric_name == metric,
                       MetricSnapshot.recorded_at >= window_2h,
                       MetricSnapshot.recorded_at < window_1h)
            )
            prev_avg = float(r2.scalar() or current_avg)
            trend = ((current_avg - prev_avg) / max(prev_avg, 0.001)) * 100
            sparkline = [float(v) for v in (values_list[-20:] if values_list else [current_avg] * 20)]

            kpis.append(DashboardKPI(
                name=metric,
                value=round(current_avg, 2),
                unit=self._unit_for(metric),
                trend=round(trend, 1),
                trend_direction="up" if trend > 0 else "down",
                sparkline=sparkline,
            ))

        response = DashboardResponse(kpis=kpis, updated_at=now)
        payload = {"kpis": [k.model_dump() for k in kpis],
                   "updated_at": now.isoformat()}
        await self.redis.setex(cache_key, 30, json.dumps(payload))
        return response

    def _unit_for(self, metric: str) -> str:
        units = {
            "cpu_utilization": "%", "memory_usage": "%",
            "request_latency_ms": "ms", "error_rate": "%",
            "throughput_rps": "rps", "queue_depth": "items",
            "disk_io_mbps": "MB/s", "network_out_mbps": "MB/s",
        }
        return units.get(metric, "")

    async def get_metric_series(self, metric_name: str, hours: int = 6) -> list[dict]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        r = await self.db.execute(
            select(MetricSnapshot.value, MetricSnapshot.recorded_at)
            .where(MetricSnapshot.metric_name == metric_name, MetricSnapshot.recorded_at >= cutoff)
            .order_by(MetricSnapshot.recorded_at)
        )
        return [{"value": row.value, "timestamp": row.recorded_at.isoformat()} for row in r.fetchall()]
