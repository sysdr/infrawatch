from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.analytics import AnalyticsEvent, HourlyMetric

_pipeline_state = {
    "status": "running",
    "events_ingested": 0,
    "events_processed": 0,
    "last_processed_at": None,
}

def get_pipeline_status() -> dict:
    return {**_pipeline_state, "checked_at": datetime.now(timezone.utc).isoformat()}

def ingest_event(db: Session, event_data: dict) -> dict:
    event = AnalyticsEvent(
        event_type  = event_data.get("event_type", "unknown"),
        user_id     = event_data.get("user_id"),
        session_id  = event_data.get("session_id"),
        page        = event_data.get("page"),
        duration_ms = event_data.get("duration_ms"),
        revenue     = event_data.get("revenue", 0.0),
        properties  = event_data.get("properties", {}),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    _pipeline_state["events_ingested"] += 1
    _pipeline_state["events_processed"] += 1
    _pipeline_state["last_processed_at"] = datetime.now(timezone.utc).isoformat()
    return {"id": event.id, "event_type": event.event_type, "status": "ingested"}

def get_event_summary(db: Session) -> dict:
    total = db.query(func.count(AnalyticsEvent.id)).scalar() or 0
    by_type = db.query(
        AnalyticsEvent.event_type,
        func.count(AnalyticsEvent.id).label("count")
    ).group_by(AnalyticsEvent.event_type).all()
    hourly_count = db.query(func.count(HourlyMetric.id)).scalar() or 0
    return {
        "total_events": total,
        "hourly_metric_rows": hourly_count,
        "by_type": {r.event_type: r.count for r in by_type},
    }
