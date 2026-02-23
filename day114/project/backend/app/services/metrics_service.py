from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from app.models.metrics import WebVitalMetric, BundleMetric, ServiceWorkerEvent
from datetime import datetime, timedelta
from typing import List, Dict, Any
import statistics

async def record_web_vitals(db: AsyncSession, metrics: List[Dict]) -> int:
    records = []
    for m in metrics:
        records.append(WebVitalMetric(
            metric_name=m.get("name"),
            value=m.get("value"),
            rating=_rate_vital(m.get("name"), m.get("value")),
            route=m.get("route", "/"),
            session_id=m.get("sessionId"),
            connection_type=m.get("connectionType"),
        ))
    db.add_all(records)
    await db.commit()
    return len(records)

async def record_bundle_metrics(db: AsyncSession, chunks: List[Dict]) -> int:
    records = [BundleMetric(**{
        "chunk_name": c.get("name"),
        "chunk_size_bytes": c.get("sizeBytes", 0),
        "load_time_ms": c.get("loadTimeMs", 0),
        "cached": c.get("cached", False),
        "route": c.get("route", "/"),
        "session_id": c.get("sessionId"),
    }) for c in chunks]
    db.add_all(records)
    await db.commit()
    return len(records)

async def record_sw_event(db: AsyncSession, event: Dict) -> None:
    record = ServiceWorkerEvent(
        event_type=event.get("type"),
        cache_strategy=event.get("strategy"),
        url=event.get("url"),
        served_from_cache=event.get("fromCache", False),
        session_id=event.get("sessionId"),
    )
    db.add(record)
    await db.commit()

async def get_vitals_summary(db: AsyncSession, hours: int = 24) -> Dict[str, Any]:
    since = datetime.utcnow() - timedelta(hours=hours)
    result = await db.execute(
        select(
            WebVitalMetric.metric_name,
            func.count(WebVitalMetric.id).label("count"),
            func.avg(WebVitalMetric.value).label("avg"),
            func.min(WebVitalMetric.value).label("min"),
            func.max(WebVitalMetric.value).label("max"),
        )
        .where(WebVitalMetric.created_at >= since)
        .group_by(WebVitalMetric.metric_name)
    )
    rows = result.all()
    summary = {}
    for row in rows:
        summary[row.metric_name] = {
            "count": row.count,
            "avg": round(row.avg, 2) if row.avg else 0,
            "min": round(row.min, 2) if row.min else 0,
            "max": round(row.max, 2) if row.max else 0,
            "rating": _rate_vital(row.metric_name, row.avg or 0),
        }
    return summary

async def get_cache_hit_ratio(db: AsyncSession, hours: int = 24) -> Dict[str, float]:
    since = datetime.utcnow() - timedelta(hours=hours)
    result = await db.execute(
        select(
            func.count(ServiceWorkerEvent.id).label("total"),
            func.sum(case((ServiceWorkerEvent.served_from_cache == True, 1), else_=0)).label("hits"),
        ).where(ServiceWorkerEvent.created_at >= since)
        .where(ServiceWorkerEvent.event_type == "fetch")
    )
    row = result.first()
    total = row.total or 0
    hits = row.hits or 0
    ratio = round((hits / total * 100), 1) if total > 0 else 0.0
    return {"total_requests": total, "cache_hits": hits, "hit_ratio_pct": ratio}

async def get_bundle_stats(db: AsyncSession) -> List[Dict]:
    result = await db.execute(
        select(
            BundleMetric.chunk_name,
            func.avg(BundleMetric.chunk_size_bytes).label("avg_size"),
            func.avg(BundleMetric.load_time_ms).label("avg_load"),
            func.count(BundleMetric.id).label("loads"),
            func.sum(case((BundleMetric.cached == True, 1), else_=0)).label("cached_loads"),
        ).group_by(BundleMetric.chunk_name)
        .order_by(func.avg(BundleMetric.chunk_size_bytes).desc())
        .limit(20)
    )
    rows = result.all()
    return [{
        "chunk": row.chunk_name,
        "avg_size_kb": round((row.avg_size or 0) / 1024, 1),
        "avg_load_ms": round(row.avg_load or 0, 1),
        "loads": row.loads,
        "cache_ratio": round((row.cached_loads / row.loads * 100) if row.loads else 0, 1),
    } for row in rows]

async def get_vitals_timeseries(db: AsyncSession, metric_name: str, hours: int = 6) -> List[Dict]:
    since = datetime.utcnow() - timedelta(hours=hours)
    result = await db.execute(
        select(WebVitalMetric.value, WebVitalMetric.created_at)
        .where(WebVitalMetric.metric_name == metric_name)
        .where(WebVitalMetric.created_at >= since)
        .order_by(WebVitalMetric.created_at)
    )
    rows = result.all()
    return [{"value": round(row.value, 2), "time": row.created_at.isoformat()} for row in rows]

def _rate_vital(name: str, value: float) -> str:
    thresholds = {
        "LCP": (2500, 4000),
        "FID": (100, 300),
        "CLS": (0.1, 0.25),
        "TTFB": (800, 1800),
        "INP": (200, 500),
    }
    if name not in thresholds:
        return "unknown"
    good, poor = thresholds[name]
    if value <= good:
        return "good"
    elif value <= poor:
        return "needs-improvement"
    return "poor"
