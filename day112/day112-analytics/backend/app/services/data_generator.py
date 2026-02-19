import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models.analytics import HourlyMetric, AnalyticsEvent

def generate_hourly_metrics(days: int = 30) -> pd.DataFrame:
    """Generate realistic 30-day hourly analytics dataset with trend + seasonality."""
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    start = now - timedelta(days=days)
    dates = pd.date_range(start=start, end=now, freq="h")
    n = len(dates)
    rng = np.random.RandomState(42)

    # Trend: gradual growth over 30 days
    trend = np.linspace(800, 1800, n)

    # Hourly seasonality: peak 10am-4pm
    hours = np.array([d.hour for d in dates])
    hourly = np.where((hours >= 9) & (hours <= 17),
                      300 * np.sin((hours - 9) * np.pi / 8), 0)

    # Weekday boost
    weekday_boost = np.where(np.array([d.dayofweek for d in dates]) < 5, 150, -80)

    noise = rng.normal(0, 60, n)
    page_views = np.maximum(trend + hourly + weekday_boost + noise, 50).astype(int)

    sessions    = np.maximum((page_views * 0.28 + rng.normal(0, 15, n)).astype(int), 5)
    revenue     = np.round(np.maximum(sessions * 5.2 + rng.normal(0, 80, n), 0), 2)
    resp_time   = np.round(80 + page_views * 0.022 + rng.normal(0, 8, n), 2)
    error_rate  = np.round(np.clip(rng.beta(1, 60, n) * 100, 0, 15), 4)

    # Inject 5 anomalies
    anomaly_idx = rng.choice(n, size=5, replace=False)
    page_views[anomaly_idx] *= rng.choice([5, 0], size=5)
    resp_time[anomaly_idx]  += rng.uniform(200, 500, 5)

    return pd.DataFrame({
        "timestamp":    dates,
        "page_views":   page_views,
        "sessions":     sessions,
        "revenue":      revenue,
        "response_time": resp_time,
        "error_rate":   error_rate,
    })

def seed_database(db: Session, days: int = 30):
    """Seed the database with generated hourly metrics and sample events."""
    existing = db.query(HourlyMetric).count()
    if existing > 0:
        return existing

    df = generate_hourly_metrics(days)
    rows = []
    for _, row in df.iterrows():
        rows.append(HourlyMetric(
            hour_bucket   = row["timestamp"],
            page_views    = int(row["page_views"]),
            sessions      = int(row["sessions"]),
            revenue       = float(row["revenue"]),
            response_time = float(row["response_time"]),
            error_rate    = float(row["error_rate"]),
        ))
    db.bulk_save_objects(rows)

    # Seed some raw events
    event_types = ["page_view", "session_start", "purchase", "signup", "click"]
    rng = np.random.RandomState(99)
    events = []
    now = datetime.now(timezone.utc)
    for i in range(200):
        etype = rng.choice(event_types)
        events.append(AnalyticsEvent(
            event_type  = etype,
            user_id     = f"user_{rng.randint(1, 50)}",
            session_id  = f"sess_{rng.randint(1, 100)}",
            page        = rng.choice(["/home", "/pricing", "/docs", "/signup"]),
            duration_ms = float(rng.randint(200, 5000)),
            revenue     = float(round(rng.uniform(0, 200), 2)) if etype == "purchase" else 0.0,
            properties  = {"source": rng.choice(["organic", "paid", "referral"])},
            created_at  = now - timedelta(hours=int(rng.randint(0, 720))),
        ))
    db.bulk_save_objects(events)
    db.commit()
    return len(rows)
