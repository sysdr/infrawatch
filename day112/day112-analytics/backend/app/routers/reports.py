from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import datetime, timedelta, timezone
from app.database import get_db
from app.models.analytics import HourlyMetric, AnalyticsEvent

router = APIRouter()

@router.get("/summary")
def report_summary(
    days: int = Query(default=7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    rows = db.query(HourlyMetric).filter(HourlyMetric.hour_bucket >= cutoff)\
             .order_by(HourlyMetric.hour_bucket).all()

    if not rows:
        return {"days": days, "summary": {}, "hourly": []}

    total_pv  = sum(r.page_views for r in rows)
    total_ses = sum(r.sessions for r in rows)
    total_rev = sum(r.revenue for r in rows)
    avg_rt    = sum(r.response_time for r in rows) / len(rows)
    avg_er    = sum(r.error_rate for r in rows) / len(rows)

    hourly = [{
        "timestamp":    r.hour_bucket.isoformat(),
        "page_views":   r.page_views,
        "sessions":     r.sessions,
        "revenue":      round(r.revenue, 2),
        "response_time": round(r.response_time, 2),
        "error_rate":   round(r.error_rate, 4),
    } for r in rows]

    return {
        "days": days,
        "summary": {
            "total_page_views":   total_pv,
            "total_sessions":     total_ses,
            "total_revenue":      round(total_rev, 2),
            "avg_response_time":  round(avg_rt, 2),
            "avg_error_rate":     round(avg_er, 4),
            "data_points":        len(rows),
        },
        "hourly": hourly,
    }

@router.get("/kpis")
def kpis(db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    this_week  = now - timedelta(days=7)
    last_week  = now - timedelta(days=14)

    def period_sum(start, end):
        rows = db.query(HourlyMetric)\
                 .filter(HourlyMetric.hour_bucket >= start,
                         HourlyMetric.hour_bucket < end).all()
        if not rows:
            return {"pv": 0, "ses": 0, "rev": 0.0, "rt": 0.0}
        return {
            "pv":  sum(r.page_views for r in rows),
            "ses": sum(r.sessions for r in rows),
            "rev": round(sum(r.revenue for r in rows), 2),
            "rt":  round(sum(r.response_time for r in rows) / len(rows), 2),
        }

    curr = period_sum(this_week, now)
    prev = period_sum(last_week, this_week)

    def pct(c, p):
        if p == 0:
            return 0.0
        return round((c - p) / p * 100, 2)

    return {
        "page_views":    {"value": curr["pv"],  "change_pct": pct(curr["pv"],  prev["pv"])},
        "sessions":      {"value": curr["ses"], "change_pct": pct(curr["ses"], prev["ses"])},
        "revenue":       {"value": curr["rev"], "change_pct": pct(curr["rev"], prev["rev"])},
        "response_time": {"value": curr["rt"],  "change_pct": pct(curr["rt"],  prev["rt"])},
    }
