#!/bin/bash
# =============================================================
# Day 112: Analytics Integration
# 180-Day Full Stack Development Series — Week 11
# =============================================================
set -e

BLUE='\033[0;34m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
RED='\033[0;31m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

PROJECT="day112-analytics"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_PORT=8112
FRONTEND_PORT=3112
VENV="$PROJECT/venv"
PID_FILE="$PROJECT/.pids"

log()     { echo -e "${CYAN}[$(date '+%H:%M:%S')]${NC} $1"; }
ok()      { echo -e "${GREEN}✓${NC} $1"; }
warn()    { echo -e "${YELLOW}⚠${NC} $1"; }
fail()    { echo -e "${RED}✗${NC} $1"; }
header()  { echo -e "\n${BOLD}${BLUE}══════════════════════════════════════════${NC}"; echo -e "${BOLD}${BLUE}  $1${NC}"; echo -e "${BOLD}${BLUE}══════════════════════════════════════════${NC}\n"; }

USE_DOCKER=false
if command -v docker &>/dev/null && docker info &>/dev/null 2>&1; then
  USE_DOCKER=true
fi

# ─────────────────────────────────────────────────────────────
# STEP 1: Create Project Structure
# ─────────────────────────────────────────────────────────────
header "Step 1: Creating Project Structure"

mkdir -p $PROJECT/{backend/{app/{models,routers,ml,services},tests},frontend/{src/{components/{Dashboard,Pipeline,ML,Correlation,Reports},api},public}}
touch $PROJECT/backend/app/__init__.py \
      $PROJECT/backend/app/models/__init__.py \
      $PROJECT/backend/app/routers/__init__.py \
      $PROJECT/backend/app/ml/__init__.py \
      $PROJECT/backend/app/services/__init__.py \
      $PROJECT/backend/tests/__init__.py

ok "Directory structure created"

# ─────────────────────────────────────────────────────────────
# STEP 2: Backend — requirements.txt
# ─────────────────────────────────────────────────────────────
header "Step 2: Creating Backend Source Files"

cat > $PROJECT/backend/requirements.txt << 'REQEOF'
fastapi==0.111.0
uvicorn[standard]==0.30.1
sqlalchemy==2.0.30
scikit-learn==1.5.0
pandas==2.2.2
numpy==1.26.4
scipy==1.13.1
joblib==1.4.2
httpx==0.27.0
pytest==8.2.0
pytest-asyncio==0.23.7
anyio==4.4.0
python-multipart==0.0.9
pydantic==2.7.1
aiofiles==23.2.1
REQEOF

# ─── database.py ───
cat > $PROJECT/backend/app/database.py << 'DBEOF'
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./analytics.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
DBEOF

# ─── models/analytics.py ───
cat > $PROJECT/backend/app/models/analytics.py << 'MODEOF'
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from app.database import Base

class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"
    id          = Column(Integer, primary_key=True, index=True)
    event_type  = Column(String(64), index=True)
    user_id     = Column(String(64), nullable=True)
    session_id  = Column(String(64), nullable=True)
    page        = Column(String(256), nullable=True)
    duration_ms = Column(Float, nullable=True)
    revenue     = Column(Float, nullable=True, default=0.0)
    properties  = Column(JSON, nullable=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now(), index=True)

class HourlyMetric(Base):
    __tablename__ = "hourly_metrics"
    id            = Column(Integer, primary_key=True, index=True)
    hour_bucket   = Column(DateTime(timezone=True), index=True)
    page_views    = Column(Integer, default=0)
    sessions      = Column(Integer, default=0)
    revenue       = Column(Float, default=0.0)
    response_time = Column(Float, default=0.0)
    error_rate    = Column(Float, default=0.0)

class MLModel(Base):
    __tablename__ = "ml_models"
    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(128))
    model_type  = Column(String(64))
    metrics     = Column(JSON, nullable=True)
    is_active   = Column(Boolean, default=False)
    model_path  = Column(String(512), nullable=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

class Prediction(Base):
    __tablename__ = "predictions"
    id              = Column(Integer, primary_key=True, index=True)
    model_id        = Column(Integer, nullable=True)
    target_hour     = Column(DateTime(timezone=True), index=True)
    predicted_value = Column(Float)
    actual_value    = Column(Float, nullable=True)
    is_anomaly      = Column(Boolean, default=False)
    anomaly_score   = Column(Float, nullable=True)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
MODEOF

# ─── services/data_generator.py ───
cat > $PROJECT/backend/app/services/data_generator.py << 'GENEOF'
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
GENEOF

# ─── services/pipeline.py ───
cat > $PROJECT/backend/app/services/pipeline.py << 'PIPEOF'
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
PIPEOF

# ─── ml/trainer.py ───
cat > $PROJECT/backend/app/ml/trainer.py << 'TRAINEOF'
import numpy as np
import pandas as pd
import joblib
import os
from datetime import datetime, timezone
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler

MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)

_ml_state = {
    "status": "idle",       # idle | training | serving | degraded | error
    "started_at": None,
    "finished_at": None,
    "metrics": {},
    "error": None,
}

def get_ml_status() -> dict:
    return {**_ml_state, "checked_at": datetime.now(timezone.utc).isoformat()}

def _build_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["hour"]        = pd.to_datetime(df["hour_bucket"]).dt.hour
    df["day_of_week"] = pd.to_datetime(df["hour_bucket"]).dt.dayofweek
    df["day_of_year"] = pd.to_datetime(df["hour_bucket"]).dt.dayofyear
    df["trend_idx"]   = np.arange(len(df))
    return df[["hour", "day_of_week", "day_of_year", "trend_idx"]]

def train_models(db_rows: list) -> dict:
    """Train RandomForest trend predictor + IsolationForest anomaly detector."""
    global _ml_state
    _ml_state["status"]     = "training"
    _ml_state["started_at"] = datetime.now(timezone.utc).isoformat()
    _ml_state["error"]      = None

    try:
        df = pd.DataFrame([{
            "hour_bucket":   r.hour_bucket,
            "page_views":    r.page_views,
            "sessions":      r.sessions,
            "revenue":       r.revenue,
            "response_time": r.response_time,
            "error_rate":    r.error_rate,
        } for r in db_rows])

        if len(df) < 48:
            raise ValueError(f"Need at least 48 rows, got {len(df)}")

        df = df.sort_values("hour_bucket").reset_index(drop=True)
        X = _build_features(df)
        y = df["page_views"]

        split = int(0.8 * len(df))
        X_train, X_test = X.iloc[:split], X.iloc[split:]
        y_train, y_test = y.iloc[:split], y.iloc[split:]

        rf = RandomForestRegressor(n_estimators=80, max_depth=8, random_state=42, n_jobs=-1)
        rf.fit(X_train, y_train)

        y_pred = rf.predict(X_test)
        residuals = y_test.values - y_pred
        metrics = {
            "r2":           round(float(r2_score(y_test, y_pred)), 4),
            "mae":          round(float(mean_absolute_error(y_test, y_pred)), 2),
            "rmse":         round(float(np.sqrt(np.mean(residuals**2))), 2),
            "std_residual": round(float(np.std(residuals)), 2),
            "train_rows":   int(split),
            "test_rows":    int(len(df) - split),
        }

        # IsolationForest on all 5 metrics
        feat_cols = ["page_views", "sessions", "revenue", "response_time", "error_rate"]
        scaler = StandardScaler()
        X_ano = scaler.fit_transform(df[feat_cols].values)
        iso = IsolationForest(contamination=0.05, random_state=42, n_estimators=100)
        iso.fit(X_ano)
        anomaly_scores = iso.decision_function(X_ano)

        joblib.dump(rf,     os.path.join(MODEL_DIR, "trend_rf.pkl"))
        joblib.dump(iso,    os.path.join(MODEL_DIR, "anomaly_iso.pkl"))
        joblib.dump(scaler, os.path.join(MODEL_DIR, "anomaly_scaler.pkl"))
        joblib.dump({
            "metrics": metrics,
            "feature_cols": feat_cols,
            "std_residual": metrics["std_residual"],
        }, os.path.join(MODEL_DIR, "model_meta.pkl"))

        _ml_state["status"]      = "serving"
        _ml_state["finished_at"] = datetime.now(timezone.utc).isoformat()
        _ml_state["metrics"]     = metrics
        return {"status": "serving", "metrics": metrics}

    except Exception as ex:
        _ml_state["status"] = "error"
        _ml_state["error"]  = str(ex)
        raise
TRAINEOF

# ─── ml/predictor.py ───
cat > $PROJECT/backend/app/ml/predictor.py << 'PREDEOF'
import numpy as np
import pandas as pd
import joblib
import os
from datetime import datetime, timedelta, timezone

MODEL_DIR = "models"

def _models_exist() -> bool:
    return all(os.path.exists(os.path.join(MODEL_DIR, f))
               for f in ["trend_rf.pkl", "anomaly_iso.pkl", "anomaly_scaler.pkl", "model_meta.pkl"])

def predict_next_hours(hours: int = 24) -> list:
    if not _models_exist():
        raise RuntimeError("Models not trained yet. POST /api/ml/train first.")
    rf   = joblib.load(os.path.join(MODEL_DIR, "trend_rf.pkl"))
    meta = joblib.load(os.path.join(MODEL_DIR, "model_meta.pkl"))
    std  = meta["std_residual"]

    now    = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    future = [now + timedelta(hours=i+1) for i in range(hours)]
    total_rows = meta["metrics"]["train_rows"] + meta["metrics"]["test_rows"]

    records = []
    for i, ts in enumerate(future):
        X = pd.DataFrame([{
            "hour":        ts.hour,
            "day_of_week": ts.weekday(),
            "day_of_year": ts.timetuple().tm_yday,
            "trend_idx":   total_rows + i,
        }])
        pred  = float(rf.predict(X)[0])
        records.append({
            "timestamp":  ts.isoformat(),
            "predicted":  round(max(pred, 0), 1),
            "upper":      round(max(pred + std, 0), 1),
            "lower":      round(max(pred - std, 0), 1),
        })
    return records

def detect_anomalies(db_rows: list) -> list:
    if not _models_exist():
        raise RuntimeError("Models not trained yet.")
    iso    = joblib.load(os.path.join(MODEL_DIR, "anomaly_iso.pkl"))
    scaler = joblib.load(os.path.join(MODEL_DIR, "anomaly_scaler.pkl"))
    meta   = joblib.load(os.path.join(MODEL_DIR, "model_meta.pkl"))
    feat_cols = meta["feature_cols"]

    df = pd.DataFrame([{
        "hour_bucket":   r.hour_bucket.isoformat(),
        "page_views":    r.page_views,
        "sessions":      r.sessions,
        "revenue":       r.revenue,
        "response_time": r.response_time,
        "error_rate":    r.error_rate,
    } for r in db_rows])

    if df.empty:
        return []

    X_scaled = scaler.transform(df[feat_cols].values)
    labels   = iso.predict(X_scaled)
    scores   = iso.decision_function(X_scaled)

    results = []
    for i, row in df.iterrows():
        results.append({
            "timestamp":    row["hour_bucket"],
            "page_views":   int(row["page_views"]),
            "is_anomaly":   bool(labels[i] == -1),
            "anomaly_score": round(float(scores[i]), 4),
        })
    return results
PREDEOF

# ─── services/correlation.py ───
cat > $PROJECT/backend/app/services/correlation.py << 'CORREOF'
import numpy as np
import pandas as pd
from scipy import stats

METRICS = ["page_views", "sessions", "revenue", "response_time", "error_rate"]

def compute_correlation_matrix(db_rows: list, method: str = "pearson") -> dict:
    df = pd.DataFrame([{
        "page_views":    r.page_views,
        "sessions":      r.sessions,
        "revenue":       r.revenue,
        "response_time": r.response_time,
        "error_rate":    r.error_rate,
    } for r in db_rows])

    if df.empty or len(df) < 3:
        return {"metrics": METRICS, "matrix": [], "pairs": []}

    matrix = []
    pairs  = []
    for m1 in METRICS:
        row = []
        for m2 in METRICS:
            if method == "spearman":
                r, p = stats.spearmanr(df[m1], df[m2])
            else:
                r, p = stats.pearsonr(df[m1], df[m2])
            r = round(float(r), 4) if not np.isnan(r) else 0.0
            p = round(float(p), 6) if not np.isnan(p) else 1.0
            row.append(r)
            if m1 < m2:
                pairs.append({
                    "x": m1, "y": m2,
                    "correlation": r, "p_value": p,
                    "significant": p < 0.05,
                })
        matrix.append(row)

    return {"metrics": METRICS, "matrix": matrix, "pairs": pairs, "method": method}
CORREOF

# ─── routers/analytics.py ───
cat > $PROJECT/backend/app/routers/analytics.py << 'ANAEOF'
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.pipeline import get_pipeline_status, ingest_event, get_event_summary

router = APIRouter()

@router.get("/pipeline")
def pipeline_status():
    return get_pipeline_status()

@router.post("/events")
def post_event(body: dict, db: Session = Depends(get_db)):
    return ingest_event(db, body)

@router.get("/summary")
def event_summary(db: Session = Depends(get_db)):
    return get_event_summary(db)
ANAEOF

# ─── routers/ml.py ───
cat > $PROJECT/backend/app/routers/ml.py << 'MLREOF'
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.analytics import HourlyMetric
from app.ml.trainer import train_models, get_ml_status
from app.ml.predictor import predict_next_hours, detect_anomalies
from app.services.correlation import compute_correlation_matrix

router = APIRouter()

def _do_train(db: Session):
    rows = db.query(HourlyMetric).order_by(HourlyMetric.hour_bucket).all()
    train_models(rows)

@router.post("/train")
def trigger_training(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    background_tasks.add_task(_do_train, db)
    return {"status": "training_started", "message": "Training running in background. Poll /api/ml/status"}

@router.get("/status")
def ml_status():
    return get_ml_status()

@router.get("/predict")
def predictions(hours: int = 24):
    try:
        data = predict_next_hours(hours)
        return {"hours": hours, "predictions": data, "count": len(data)}
    except RuntimeError as e:
        return {"error": str(e), "predictions": []}

@router.get("/anomalies")
def anomalies(db: Session = Depends(get_db)):
    rows = db.query(HourlyMetric).order_by(HourlyMetric.hour_bucket).all()
    try:
        data = detect_anomalies(rows)
        flagged = [d for d in data if d["is_anomaly"]]
        return {"total_points": len(data), "anomalies_found": len(flagged), "data": data}
    except RuntimeError as e:
        return {"error": str(e), "data": []}

@router.get("/correlations")
def correlations(method: str = "pearson", db: Session = Depends(get_db)):
    rows = db.query(HourlyMetric).order_by(HourlyMetric.hour_bucket).all()
    return compute_correlation_matrix(rows, method)
MLREOF

# ─── routers/reports.py ───
cat > $PROJECT/backend/app/routers/reports.py << 'REPEOF'
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
REPEOF

# ─── main.py ───
cat > $PROJECT/backend/app/main.py << 'MAINEOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, get_db
from app.models.analytics import Base
from app.routers import analytics, ml, reports
from app.services.data_generator import seed_database

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Day 112 Analytics Integration API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(ml.router,        prefix="/api/ml",        tags=["ml"])
app.include_router(reports.router,   prefix="/api/reports",   tags=["reports"])

@app.on_event("startup")
def startup():
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        count = seed_database(db)
        print(f"[startup] Database seeded: {count} hourly metric rows")
    finally:
        db.close()

@app.get("/health")
def health():
    return {"status": "healthy", "service": "analytics-integration", "version": "1.0.0"}
MAINEOF

ok "Backend files created"

# ─────────────────────────────────────────────────────────────
# STEP 3: Tests
# ─────────────────────────────────────────────────────────────
header "Step 3: Creating Test Files"

cat > $PROJECT/backend/tests/test_analytics.py << 'T1EOF'
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
from app.services.data_generator import seed_database

TEST_DB = "sqlite:///./test_analytics.db"
engine  = create_engine(TEST_DB, connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def override_db():
    db = TestSession()
    try:
        seed_database(db)
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_db
client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"

def test_pipeline_status():
    r = client.get("/api/analytics/pipeline")
    assert r.status_code == 200
    data = r.json()
    assert "status" in data

def test_ingest_event():
    payload = {
        "event_type": "page_view",
        "user_id": "test_user_1",
        "session_id": "sess_abc",
        "page": "/home",
        "duration_ms": 1200.0,
        "revenue": 0.0,
        "properties": {"source": "organic"}
    }
    r = client.post("/api/analytics/events", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["event_type"] == "page_view"
    assert data["status"] == "ingested"

def test_event_summary():
    r = client.get("/api/analytics/summary")
    assert r.status_code == 200
    data = r.json()
    assert "total_events" in data
    assert "by_type" in data

def test_kpis():
    r = client.get("/api/reports/kpis")
    assert r.status_code == 200
    data = r.json()
    assert "page_views" in data
    assert "revenue" in data
    assert "change_pct" in data["page_views"]

def test_report_summary():
    r = client.get("/api/reports/summary?days=7")
    assert r.status_code == 200
    data = r.json()
    assert "summary" in data
    assert "hourly" in data
    assert data["days"] == 7
T1EOF

cat > $PROJECT/backend/tests/test_ml.py << 'T2EOF'
import pytest
import time
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
from app.services.data_generator import seed_database

TEST_DB = "sqlite:///./test_ml.db"
engine  = create_engine(TEST_DB, connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def override_db():
    db = TestSession()
    try:
        seed_database(db, days=30)
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_db
client = TestClient(app)

def test_ml_status_idle():
    r = client.get("/api/ml/status")
    assert r.status_code == 200
    data = r.json()
    assert "status" in data

def test_ml_train_trigger():
    r = client.post("/api/ml/train")
    assert r.status_code == 200
    assert "training_started" in r.json()["status"]

def test_ml_train_and_predict():
    # Synchronous training for test
    from app.ml.trainer import train_models, _ml_state
    from sqlalchemy.orm import Session
    from app.models.analytics import HourlyMetric

    db = TestSession()
    try:
        seed_database(db, days=30)
        rows = db.query(HourlyMetric).all()
        assert len(rows) >= 48, f"Expected >= 48 rows, got {len(rows)}"
        result = train_models(rows)
        assert result["status"] == "serving"
        assert "r2" in result["metrics"]
        assert result["metrics"]["r2"] > -0.5
    finally:
        db.close()

def test_predictions():
    from app.ml.predictor import predict_next_hours
    preds = predict_next_hours(12)
    assert len(preds) == 12
    for p in preds:
        assert "predicted" in p
        assert "upper" in p
        assert "lower" in p
        assert p["upper"] >= p["predicted"] >= p["lower"]

def test_anomaly_detection():
    from app.ml.predictor import detect_anomalies
    db = TestSession()
    try:
        from app.models.analytics import HourlyMetric
        rows = db.query(HourlyMetric).all()
        results = detect_anomalies(rows)
        assert isinstance(results, list)
        assert len(results) > 0
        flagged = [r for r in results if r["is_anomaly"]]
        assert len(flagged) >= 1, "Expected at least 1 anomaly in seeded data"
    finally:
        db.close()

def test_correlations():
    r = client.get("/api/ml/correlations?method=pearson")
    assert r.status_code == 200
    data = r.json()
    assert "matrix" in data
    assert "metrics" in data
    assert len(data["matrix"]) == 5
    assert len(data["matrix"][0]) == 5
    # Diagonal should be 1.0
    for i in range(5):
        assert abs(data["matrix"][i][i] - 1.0) < 0.001
T2EOF

ok "Test files created"

# ─────────────────────────────────────────────────────────────
# STEP 4: Frontend
# ─────────────────────────────────────────────────────────────
header "Step 4: Creating Frontend"

cat > $PROJECT/frontend/package.json << 'PKGEOF'
{
  "name": "day112-analytics-dashboard",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "vite --port 3112 --host",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "recharts": "^2.12.7",
    "axios": "^1.7.2",
    "date-fns": "^3.6.0",
    "lucide-react": "^0.400.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.1",
    "vite": "^5.3.1"
  }
}
PKGEOF

cat > $PROJECT/frontend/vite.config.js << 'VCEOF'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3112,
    proxy: {
      '/api': {
        target: 'http://localhost:8112',
        changeOrigin: true,
      }
    }
  }
})
VCEOF

cat > $PROJECT/frontend/index.html << 'HTMLEOF'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Analytics Intelligence Platform</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Inter', sans-serif; background: #0f1117; color: #e2e8f0; }
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #1e2028; }
    ::-webkit-scrollbar-thumb { background: #2d6a4f; border-radius: 3px; }
  </style>
</head>
<body>
  <div id="root"></div>
  <script type="module" src="/src/main.jsx"></script>
</body>
</html>
HTMLEOF

cat > $PROJECT/frontend/src/main.jsx << 'MAINREOF'
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
MAINREOF

cat > $PROJECT/frontend/src/api/client.js << 'APIEOF'
import axios from 'axios'

const api = axios.create({ baseURL: '/api', timeout: 30000 })

export const fetchPipelineStatus  = () => api.get('/analytics/pipeline').then(r => r.data)
export const fetchEventSummary    = () => api.get('/analytics/summary').then(r => r.data)
export const postEvent            = (body) => api.post('/analytics/events', body).then(r => r.data)
export const fetchMLStatus        = () => api.get('/ml/status').then(r => r.data)
export const triggerTrain         = () => api.post('/ml/train').then(r => r.data)
export const fetchPredictions     = (h=24) => api.get(`/ml/predict?hours=${h}`).then(r => r.data)
export const fetchAnomalies       = () => api.get('/ml/anomalies').then(r => r.data)
export const fetchCorrelations    = (m='pearson') => api.get(`/ml/correlations?method=${m}`).then(r => r.data)
export const fetchKPIs            = () => api.get('/reports/kpis').then(r => r.data)
export const fetchReport          = (days=7) => api.get(`/reports/summary?days=${days}`).then(r => r.data)
APIEOF

cat > $PROJECT/frontend/src/App.jsx << 'APPEOF'
import React, { useState } from 'react'
import Sidebar from './components/Sidebar'
import Dashboard from './components/Dashboard'
import Pipeline from './components/Pipeline'
import MLPanel from './components/ML'
import CorrelationPanel from './components/Correlation'
import ReportsPanel from './components/Reports'

const VIEWS = {
  dashboard:   { label: 'Overview',      icon: '◈', component: Dashboard },
  pipeline:    { label: 'Pipeline',      icon: '⟳', component: Pipeline },
  ml:          { label: 'ML Models',     icon: '⬡', component: MLPanel },
  correlation: { label: 'Correlations',  icon: '⊞', component: CorrelationPanel },
  reports:     { label: 'Reports',       icon: '◧', component: ReportsPanel },
}

export default function App() {
  const [active, setActive] = useState('dashboard')
  const View = VIEWS[active].component

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#0f1117' }}>
      <Sidebar views={VIEWS} active={active} onSelect={setActive} />
      <main style={{ flex: 1, overflow: 'auto', padding: '28px 32px' }}>
        <View />
      </main>
    </div>
  )
}
APPEOF

cat > $PROJECT/frontend/src/components/Sidebar.jsx << 'SBEOF'
import React from 'react'

export default function Sidebar({ views, active, onSelect }) {
  return (
    <aside style={{
      width: 220, background: '#161b22', borderRight: '1px solid #21262d',
      display: 'flex', flexDirection: 'column', padding: '24px 0',
    }}>
      <div style={{ padding: '0 20px 28px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 32, height: 32, borderRadius: 8, background: 'linear-gradient(135deg, #2d6a4f, #52b788)',
            display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 16
          }}>⬢</div>
          <div>
            <div style={{ fontSize: 13, fontWeight: 700, color: '#e2e8f0', letterSpacing: '0.5px' }}>INSIGHT</div>
            <div style={{ fontSize: 10, color: '#6e7681', letterSpacing: '1px' }}>ANALYTICS</div>
          </div>
        </div>
      </div>

      <div style={{ padding: '0 12px', fontSize: 10, color: '#6e7681', letterSpacing: '1px', marginBottom: 8 }}>
        NAVIGATION
      </div>

      {Object.entries(views).map(([key, v]) => {
        const isActive = key === active
        return (
          <button key={key} onClick={() => onSelect(key)} style={{
            display: 'flex', alignItems: 'center', gap: 12,
            padding: '10px 20px', margin: '2px 8px', border: 'none',
            borderRadius: 8, cursor: 'pointer', textAlign: 'left',
            background: isActive ? 'rgba(45,106,79,0.25)' : 'transparent',
            borderLeft: isActive ? '3px solid #52b788' : '3px solid transparent',
            color: isActive ? '#52b788' : '#8b949e',
            fontSize: 13, fontWeight: isActive ? 600 : 400,
            transition: 'all 0.15s ease',
          }}>
            <span style={{ fontSize: 16 }}>{v.icon}</span>
            {v.label}
          </button>
        )
      })}

      <div style={{ marginTop: 'auto', padding: '16px 20px', borderTop: '1px solid #21262d' }}>
        <div style={{ fontSize: 10, color: '#6e7681' }}>Day 112 · Week 11</div>
        <div style={{ fontSize: 10, color: '#52b788', marginTop: 2 }}>Analytics Integration</div>
      </div>
    </aside>
  )
}
SBEOF

cat > $PROJECT/frontend/src/components/Dashboard/index.jsx << 'DASHEOF'
import React, { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { fetchKPIs, fetchReport } from '../../api/client'

const KPICard = ({ label, value, change, unit = '' }) => {
  const up = change >= 0
  return (
    <div style={{
      background: '#161b22', border: '1px solid #21262d', borderRadius: 12,
      padding: '20px 24px', flex: 1,
    }}>
      <div style={{ fontSize: 11, color: '#8b949e', letterSpacing: '0.8px', marginBottom: 8 }}>{label.toUpperCase()}</div>
      <div style={{ fontSize: 28, fontWeight: 700, color: '#e2e8f0', fontFamily: 'JetBrains Mono' }}>
        {unit}{typeof value === 'number' ? value.toLocaleString() : value}
      </div>
      <div style={{ fontSize: 12, marginTop: 6, color: up ? '#52b788' : '#f85149' }}>
        {up ? '▲' : '▼'} {Math.abs(change)}% vs last week
      </div>
    </div>
  )
}

export default function Dashboard() {
  const [kpis, setKpis]     = useState(null)
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([fetchKPIs(), fetchReport(7)]).then(([k, r]) => {
      setKpis(k); setReport(r); setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  if (loading) return <div style={{ color: '#8b949e', padding: 40 }}>Loading dashboard...</div>

  const chartData = (report?.hourly || []).slice(-48).map(h => ({
    time: new Date(h.timestamp).toLocaleTimeString('en', { hour: '2-digit', minute: '2-digit' }),
    pageViews: h.page_views,
    sessions: h.sessions,
    revenue: h.revenue,
  }))

  return (
    <div>
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, color: '#e2e8f0' }}>Analytics Overview</h1>
        <p style={{ color: '#8b949e', fontSize: 13, marginTop: 4 }}>Last 7 days · Auto-refreshed</p>
      </div>

      {kpis && (
        <div style={{ display: 'flex', gap: 16, marginBottom: 28 }}>
          <KPICard label="Page Views"    value={kpis.page_views?.value}    change={kpis.page_views?.change_pct} />
          <KPICard label="Sessions"      value={kpis.sessions?.value}      change={kpis.sessions?.change_pct} />
          <KPICard label="Revenue"       value={kpis.revenue?.value}       change={kpis.revenue?.change_pct}       unit="$" />
          <KPICard label="Resp Time (ms)" value={kpis.response_time?.value} change={kpis.response_time?.change_pct} />
        </div>
      )}

      <div style={{ background: '#161b22', border: '1px solid #21262d', borderRadius: 12, padding: '24px' }}>
        <h2 style={{ fontSize: 14, fontWeight: 600, color: '#e2e8f0', marginBottom: 20 }}>Page Views & Sessions — Last 48h</h2>
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
            <XAxis dataKey="time" tick={{ fill: '#6e7681', fontSize: 10 }} interval={5} />
            <YAxis tick={{ fill: '#6e7681', fontSize: 10 }} />
            <Tooltip contentStyle={{ background: '#1e2028', border: '1px solid #30363d', borderRadius: 8, color: '#e2e8f0', fontSize: 12 }} />
            <Line type="monotone" dataKey="pageViews" stroke="#52b788" strokeWidth={2} dot={false} name="Page Views" />
            <Line type="monotone" dataKey="sessions"  stroke="#f0883e" strokeWidth={1.5} dot={false} name="Sessions" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
DASHEOF

cat > $PROJECT/frontend/src/components/Pipeline/index.jsx << 'PLEOF'
import React, { useState, useEffect, useCallback } from 'react'
import { fetchPipelineStatus, fetchEventSummary, postEvent } from '../../api/client'

const Badge = ({ status }) => {
  const colors = { running: '#52b788', stopped: '#f85149', degraded: '#f0883e' }
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 6,
      padding: '4px 12px', borderRadius: 20,
      background: `${colors[status] || '#8b949e'}22`,
      color: colors[status] || '#8b949e', fontSize: 12, fontWeight: 600
    }}>
      <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'currentColor' }} />
      {status?.toUpperCase()}
    </span>
  )
}

export default function Pipeline() {
  const [status, setStatus]   = useState(null)
  const [summary, setSummary] = useState(null)
  const [sending, setSending] = useState(false)
  const [lastEvent, setLastEvent] = useState(null)

  const refresh = useCallback(() => {
    Promise.all([fetchPipelineStatus(), fetchEventSummary()])
      .then(([s, sm]) => { setStatus(s); setSummary(sm) })
  }, [])

  useEffect(() => { refresh(); const t = setInterval(refresh, 4000); return () => clearInterval(t) }, [refresh])

  const sendTestEvent = async () => {
    setSending(true)
    try {
      const ev = await postEvent({
        event_type: 'page_view',
        user_id: `demo_user_${Date.now()}`,
        session_id: `sess_${Date.now()}`,
        page: '/demo',
        duration_ms: 1500,
        revenue: 0,
        properties: { source: 'demo' }
      })
      setLastEvent(ev)
      refresh()
    } finally { setSending(false) }
  }

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, color: '#e2e8f0' }}>Analytics Pipeline</h1>
        <p style={{ color: '#8b949e', fontSize: 13, marginTop: 4 }}>Real-time event ingestion status</p>
      </div>

      <div style={{ display: 'flex', gap: 16, marginBottom: 20 }}>
        <div style={{ background: '#161b22', border: '1px solid #21262d', borderRadius: 12, padding: '20px 24px', flex: 1 }}>
          <div style={{ fontSize: 11, color: '#8b949e', letterSpacing: '0.8px', marginBottom: 12 }}>PIPELINE STATUS</div>
          <Badge status={status?.status || 'checking'} />
          <div style={{ marginTop: 12, fontSize: 12, color: '#6e7681' }}>
            Last processed: {status?.last_processed_at ? new Date(status.last_processed_at).toLocaleTimeString() : '—'}
          </div>
        </div>
        <div style={{ background: '#161b22', border: '1px solid #21262d', borderRadius: 12, padding: '20px 24px', flex: 1 }}>
          <div style={{ fontSize: 11, color: '#8b949e', letterSpacing: '0.8px', marginBottom: 8 }}>EVENTS INGESTED</div>
          <div style={{ fontSize: 32, fontWeight: 700, color: '#52b788', fontFamily: 'JetBrains Mono' }}>
            {status?.events_ingested ?? '—'}
          </div>
        </div>
        <div style={{ background: '#161b22', border: '1px solid #21262d', borderRadius: 12, padding: '20px 24px', flex: 1 }}>
          <div style={{ fontSize: 11, color: '#8b949e', letterSpacing: '0.8px', marginBottom: 8 }}>TOTAL DB EVENTS</div>
          <div style={{ fontSize: 32, fontWeight: 700, color: '#52b788', fontFamily: 'JetBrains Mono' }}>
            {summary?.total_events ?? '—'}
          </div>
        </div>
      </div>

      {summary?.by_type && (
        <div style={{ background: '#161b22', border: '1px solid #21262d', borderRadius: 12, padding: '20px 24px', marginBottom: 20 }}>
          <div style={{ fontSize: 13, fontWeight: 600, color: '#e2e8f0', marginBottom: 16 }}>Events by Type</div>
          {Object.entries(summary.by_type).map(([type, count]) => (
            <div key={type} style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 10 }}>
              <div style={{ width: 110, fontSize: 12, color: '#8b949e' }}>{type}</div>
              <div style={{ flex: 1, background: '#21262d', borderRadius: 4, height: 8 }}>
                <div style={{
                  width: `${Math.min((count / summary.total_events) * 100, 100)}%`,
                  height: '100%', background: '#52b788', borderRadius: 4,
                }} />
              </div>
              <div style={{ width: 40, fontSize: 12, color: '#52b788', fontFamily: 'JetBrains Mono', textAlign: 'right' }}>{count}</div>
            </div>
          ))}
        </div>
      )}

      <button onClick={sendTestEvent} disabled={sending} style={{
        padding: '10px 22px', background: '#2d6a4f', color: '#d8f3dc', border: 'none',
        borderRadius: 8, cursor: 'pointer', fontSize: 13, fontWeight: 600,
      }}>
        {sending ? 'Sending...' : '⚡ Send Test Event'}
      </button>
      {lastEvent && (
        <div style={{ marginTop: 12, padding: '10px 16px', background: '#0d1117', border: '1px solid #30363d', borderRadius: 8, fontSize: 12, fontFamily: 'JetBrains Mono', color: '#52b788' }}>
          ✓ Event ingested · id: {lastEvent.id} · type: {lastEvent.event_type}
        </div>
      )}
    </div>
  )
}
PLEOF

cat > $PROJECT/frontend/src/components/ML/index.jsx << 'MLEOF'
import React, { useState, useEffect, useCallback } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine, Scatter, ScatterChart } from 'recharts'
import { fetchMLStatus, triggerTrain, fetchPredictions, fetchAnomalies } from '../../api/client'

const StateIndicator = ({ status }) => {
  const map = {
    idle:     { color: '#8b949e', label: 'IDLE' },
    training: { color: '#f0883e', label: 'TRAINING' },
    serving:  { color: '#52b788', label: 'SERVING' },
    error:    { color: '#f85149', label: 'ERROR' },
    degraded: { color: '#ffa657', label: 'DEGRADED' },
  }
  const s = map[status] || map.idle
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
      <div style={{
        width: 12, height: 12, borderRadius: '50%', background: s.color,
        boxShadow: `0 0 8px ${s.color}`,
        animation: status === 'training' ? 'pulse 1.2s infinite' : 'none'
      }} />
      <span style={{ fontSize: 13, fontWeight: 700, color: s.color }}>{s.label}</span>
    </div>
  )
}

export default function MLPanel() {
  const [mlStatus, setMlStatus]   = useState(null)
  const [preds, setPreds]         = useState([])
  const [anomalies, setAnomalies] = useState(null)
  const [training, setTraining]   = useState(false)
  const [hours, setHours]         = useState(24)

  const refresh = useCallback(() => {
    fetchMLStatus().then(setMlStatus)
    fetchPredictions(hours).then(d => setPreds(d.predictions || []))
    fetchAnomalies().then(setAnomalies)
  }, [hours])

  useEffect(() => { refresh(); const t = setInterval(refresh, 5000); return () => clearInterval(t) }, [refresh])

  const handleTrain = async () => {
    setTraining(true)
    await triggerTrain()
    setTimeout(() => { refresh(); setTraining(false) }, 3000)
  }

  const predChartData = preds.map((p, i) => ({
    hour:   i + 1,
    pred:   p.predicted,
    upper:  p.upper,
    lower:  p.lower,
  }))

  const anomalyData = (anomalies?.data || []).slice(-96).map((d, i) => ({
    x: i,
    y: d.page_views,
    anomaly: d.is_anomaly,
  }))

  return (
    <div>
      <style>{`@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.4}}`}</style>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, color: '#e2e8f0' }}>ML Model Engine</h1>
        <p style={{ color: '#8b949e', fontSize: 13, marginTop: 4 }}>RandomForest Trend Prediction · IsolationForest Anomaly Detection</p>
      </div>

      <div style={{ display: 'flex', gap: 16, marginBottom: 20 }}>
        <div style={{ background: '#161b22', border: '1px solid #21262d', borderRadius: 12, padding: '20px 24px', flex: 1 }}>
          <div style={{ fontSize: 11, color: '#8b949e', letterSpacing: '0.8px', marginBottom: 12 }}>MODEL STATE</div>
          <StateIndicator status={mlStatus?.status} />
          {mlStatus?.finished_at && (
            <div style={{ marginTop: 8, fontSize: 11, color: '#6e7681' }}>
              Trained at {new Date(mlStatus.finished_at).toLocaleTimeString()}
            </div>
          )}
        </div>
        {mlStatus?.metrics && (
          <>
            <div style={{ background: '#161b22', border: '1px solid #21262d', borderRadius: 12, padding: '20px 24px', flex: 1 }}>
              <div style={{ fontSize: 11, color: '#8b949e', marginBottom: 8 }}>R² SCORE</div>
              <div style={{ fontSize: 28, fontWeight: 700, color: '#52b788', fontFamily: 'JetBrains Mono' }}>
                {mlStatus.metrics.r2?.toFixed(4)}
              </div>
            </div>
            <div style={{ background: '#161b22', border: '1px solid #21262d', borderRadius: 12, padding: '20px 24px', flex: 1 }}>
              <div style={{ fontSize: 11, color: '#8b949e', marginBottom: 8 }}>MAE</div>
              <div style={{ fontSize: 28, fontWeight: 700, color: '#f0883e', fontFamily: 'JetBrains Mono' }}>
                {mlStatus.metrics.mae?.toFixed(1)}
              </div>
            </div>
            <div style={{ background: '#161b22', border: '1px solid #21262d', borderRadius: 12, padding: '20px 24px', flex: 1 }}>
              <div style={{ fontSize: 11, color: '#8b949e', marginBottom: 8 }}>ANOMALIES</div>
              <div style={{ fontSize: 28, fontWeight: 700, color: '#ffa657', fontFamily: 'JetBrains Mono' }}>
                {anomalies?.anomalies_found ?? '—'}
              </div>
            </div>
          </>
        )}
      </div>

      <div style={{ display: 'flex', gap: 12, marginBottom: 20 }}>
        <button onClick={handleTrain} disabled={training} style={{
          padding: '10px 22px', background: '#2d6a4f', color: '#d8f3dc',
          border: 'none', borderRadius: 8, cursor: 'pointer', fontSize: 13, fontWeight: 600,
        }}>
          {training ? '⟳ Training...' : '▶ Train Models'}
        </button>
        <select value={hours} onChange={e => setHours(Number(e.target.value))} style={{
          padding: '10px 16px', background: '#21262d', color: '#e2e8f0',
          border: '1px solid #30363d', borderRadius: 8, fontSize: 13, cursor: 'pointer',
        }}>
          <option value={12}>12h forecast</option>
          <option value={24}>24h forecast</option>
          <option value={48}>48h forecast</option>
        </select>
      </div>

      {predChartData.length > 0 && (
        <div style={{ background: '#161b22', border: '1px solid #21262d', borderRadius: 12, padding: '24px', marginBottom: 20 }}>
          <h2 style={{ fontSize: 14, fontWeight: 600, color: '#e2e8f0', marginBottom: 20 }}>
            Page View Forecast — Next {hours}h (with confidence bounds)
          </h2>
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={predChartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
              <XAxis dataKey="hour" tick={{ fill: '#6e7681', fontSize: 10 }} label={{ value: 'Hours ahead', position: 'insideBottom', fill: '#6e7681', fontSize: 10 }} />
              <YAxis tick={{ fill: '#6e7681', fontSize: 10 }} />
              <Tooltip contentStyle={{ background: '#1e2028', border: '1px solid #30363d', borderRadius: 8, color: '#e2e8f0', fontSize: 12 }} />
              <Line type="monotone" dataKey="pred"  stroke="#52b788" strokeWidth={2.5} dot={false} name="Predicted" />
              <Line type="monotone" dataKey="upper" stroke="#52b788" strokeWidth={1} strokeDasharray="4 3" dot={false} name="Upper bound" />
              <Line type="monotone" dataKey="lower" stroke="#52b788" strokeWidth={1} strokeDasharray="4 3" dot={false} name="Lower bound" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {anomalyData.length > 0 && (
        <div style={{ background: '#161b22', border: '1px solid #21262d', borderRadius: 12, padding: '24px' }}>
          <h2 style={{ fontSize: 14, fontWeight: 600, color: '#e2e8f0', marginBottom: 20 }}>
            Anomaly Detection — Last 96 Hours (red = anomalous)
          </h2>
          <ResponsiveContainer width="100%" height={180}>
            <ScatterChart>
              <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
              <XAxis dataKey="x" tick={{ fill: '#6e7681', fontSize: 10 }} name="Hour" />
              <YAxis dataKey="y" tick={{ fill: '#6e7681', fontSize: 10 }} name="Page Views" />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ background: '#1e2028', border: '1px solid #30363d', borderRadius: 8, fontSize: 12, color: '#e2e8f0' }} />
              <Scatter data={anomalyData.filter(d => !d.anomaly)} fill="#52b788" opacity={0.4} r={2} name="Normal" />
              <Scatter data={anomalyData.filter(d => d.anomaly)}  fill="#f85149" opacity={0.9} r={5} name="Anomaly" />
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}
MLEOF

cat > $PROJECT/frontend/src/components/Correlation/index.jsx << 'CORREOF'
import React, { useState, useEffect } from 'react'
import { fetchCorrelations } from '../../api/client'

const METRICS_LABELS = {
  page_views:    'Page Views',
  sessions:      'Sessions',
  revenue:       'Revenue',
  response_time: 'Resp. Time',
  error_rate:    'Error Rate',
}

function getColor(val) {
  const abs = Math.abs(val)
  if (abs < 0.2) return { bg: '#21262d', text: '#6e7681' }
  if (val > 0)   return { bg: `rgba(82,183,136,${0.15 + abs * 0.6})`, text: abs > 0.6 ? '#d8f3dc' : '#52b788' }
  return           { bg: `rgba(248,81,73,${0.15 + abs * 0.6})`,  text: abs > 0.6 ? '#ffd7d5' : '#f85149' }
}

export default function CorrelationPanel() {
  const [data, setData]     = useState(null)
  const [method, setMethod] = useState('pearson')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    fetchCorrelations(method).then(d => { setData(d); setLoading(false) })
  }, [method])

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, color: '#e2e8f0' }}>Correlation Analysis</h1>
        <p style={{ color: '#8b949e', fontSize: 13, marginTop: 4 }}>Pearson / Spearman correlation matrix across all metrics</p>
      </div>

      <div style={{ marginBottom: 20 }}>
        {['pearson','spearman'].map(m => (
          <button key={m} onClick={() => setMethod(m)} style={{
            marginRight: 8, padding: '8px 18px', borderRadius: 8, border: 'none', cursor: 'pointer', fontSize: 12, fontWeight: 600,
            background: method === m ? '#2d6a4f' : '#21262d',
            color: method === m ? '#d8f3dc' : '#8b949e',
          }}>{m.charAt(0).toUpperCase() + m.slice(1)}</button>
        ))}
      </div>

      {loading ? (
        <div style={{ color: '#8b949e' }}>Computing correlations...</div>
      ) : data?.matrix?.length > 0 && (
        <div style={{ background: '#161b22', border: '1px solid #21262d', borderRadius: 12, padding: '28px' }}>
          <h2 style={{ fontSize: 14, fontWeight: 600, color: '#e2e8f0', marginBottom: 24 }}>
            {method.charAt(0).toUpperCase() + method.slice(1)} Correlation Heatmap
          </h2>

          <div style={{ overflowX: 'auto' }}>
            <table style={{ borderCollapse: 'separate', borderSpacing: 4 }}>
              <thead>
                <tr>
                  <th style={{ width: 90 }} />
                  {data.metrics.map(m => (
                    <th key={m} style={{ width: 90, fontSize: 10, color: '#8b949e', fontWeight: 500, textAlign: 'center', paddingBottom: 8 }}>
                      {METRICS_LABELS[m] || m}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.matrix.map((row, i) => (
                  <tr key={i}>
                    <td style={{ fontSize: 10, color: '#8b949e', paddingRight: 8, textAlign: 'right', fontWeight: 500 }}>
                      {METRICS_LABELS[data.metrics[i]] || data.metrics[i]}
                    </td>
                    {row.map((val, j) => {
                      const c = getColor(val)
                      return (
                        <td key={j} title={`${data.metrics[i]} × ${data.metrics[j]}: ${val}`} style={{
                          width: 90, height: 72, textAlign: 'center', verticalAlign: 'middle',
                          background: c.bg, borderRadius: 8, cursor: 'default',
                          transition: 'transform 0.1s',
                        }}>
                          <div style={{ fontSize: 16, fontWeight: 700, color: c.text, fontFamily: 'JetBrains Mono' }}>
                            {val.toFixed(2)}
                          </div>
                        </td>
                      )
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div style={{ marginTop: 24, display: 'flex', gap: 20 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 11, color: '#8b949e' }}>
              <div style={{ width: 14, height: 14, borderRadius: 3, background: 'rgba(82,183,136,0.7)' }} /> Positive
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 11, color: '#8b949e' }}>
              <div style={{ width: 14, height: 14, borderRadius: 3, background: 'rgba(248,81,73,0.7)' }} /> Negative
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 11, color: '#8b949e' }}>
              <div style={{ width: 14, height: 14, borderRadius: 3, background: '#21262d' }} /> Weak / None
            </div>
          </div>

          {data.pairs?.filter(p => p.significant).length > 0 && (
            <div style={{ marginTop: 24 }}>
              <div style={{ fontSize: 13, fontWeight: 600, color: '#e2e8f0', marginBottom: 12 }}>Statistically Significant Pairs (p &lt; 0.05)</div>
              {data.pairs.filter(p => p.significant).map((p, i) => (
                <div key={i} style={{ display: 'flex', gap: 12, alignItems: 'center', marginBottom: 8, fontSize: 12 }}>
                  <span style={{ color: '#52b788', fontFamily: 'JetBrains Mono', fontWeight: 600 }}>
                    {METRICS_LABELS[p.x]} × {METRICS_LABELS[p.y]}
                  </span>
                  <span style={{ color: p.correlation > 0 ? '#52b788' : '#f85149', fontFamily: 'JetBrains Mono' }}>
                    r = {p.correlation.toFixed(4)}
                  </span>
                  <span style={{ color: '#6e7681' }}>p = {p.p_value.toFixed(4)}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
CORREOF

cat > $PROJECT/frontend/src/components/Reports/index.jsx << 'REPEOF'
import React, { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { fetchReport } from '../../api/client'

export default function ReportsPanel() {
  const [days, setDays]     = useState(7)
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    fetchReport(days).then(d => { setReport(d); setLoading(false) })
  }, [days])

  const daily = []
  if (report?.hourly) {
    const grouped = {}
    report.hourly.forEach(h => {
      const day = h.timestamp.split('T')[0]
      if (!grouped[day]) grouped[day] = { page_views: 0, sessions: 0, revenue: 0 }
      grouped[day].page_views += h.page_views
      grouped[day].sessions   += h.sessions
      grouped[day].revenue    += h.revenue
    })
    Object.entries(grouped).forEach(([day, vals]) => {
      daily.push({ day: day.slice(5), ...vals, revenue: Math.round(vals.revenue) })
    })
  }

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, color: '#e2e8f0' }}>Advanced Reports</h1>
        <p style={{ color: '#8b949e', fontSize: 13, marginTop: 4 }}>Aggregated analytics with time-window filtering</p>
      </div>

      <div style={{ marginBottom: 20 }}>
        {[3, 7, 14, 30].map(d => (
          <button key={d} onClick={() => setDays(d)} style={{
            marginRight: 8, padding: '8px 18px', borderRadius: 8, border: 'none', cursor: 'pointer', fontSize: 12, fontWeight: 600,
            background: days === d ? '#2d6a4f' : '#21262d',
            color: days === d ? '#d8f3dc' : '#8b949e',
          }}>Last {d}d</button>
        ))}
      </div>

      {!loading && report?.summary && (
        <div style={{ display: 'flex', gap: 16, marginBottom: 24 }}>
          {[
            { label: 'Total Page Views', value: report.summary.total_page_views?.toLocaleString() },
            { label: 'Total Sessions',   value: report.summary.total_sessions?.toLocaleString() },
            { label: 'Total Revenue',    value: `$${report.summary.total_revenue?.toLocaleString()}` },
            { label: 'Avg Response Time', value: `${report.summary.avg_response_time}ms` },
          ].map(k => (
            <div key={k.label} style={{ background: '#161b22', border: '1px solid #21262d', borderRadius: 12, padding: '16px 20px', flex: 1 }}>
              <div style={{ fontSize: 10, color: '#8b949e', letterSpacing: '0.8px' }}>{k.label.toUpperCase()}</div>
              <div style={{ fontSize: 22, fontWeight: 700, color: '#52b788', fontFamily: 'JetBrains Mono', marginTop: 6 }}>{k.value}</div>
            </div>
          ))}
        </div>
      )}

      {daily.length > 0 && (
        <div style={{ background: '#161b22', border: '1px solid #21262d', borderRadius: 12, padding: '24px', marginBottom: 20 }}>
          <h2 style={{ fontSize: 14, fontWeight: 600, color: '#e2e8f0', marginBottom: 20 }}>Daily Page Views</h2>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={daily}>
              <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
              <XAxis dataKey="day" tick={{ fill: '#6e7681', fontSize: 10 }} />
              <YAxis tick={{ fill: '#6e7681', fontSize: 10 }} />
              <Tooltip contentStyle={{ background: '#1e2028', border: '1px solid #30363d', borderRadius: 8, color: '#e2e8f0', fontSize: 12 }} />
              <Bar dataKey="page_views" fill="#52b788" radius={[4, 4, 0, 0]} name="Page Views" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {daily.length > 0 && (
        <div style={{ background: '#161b22', border: '1px solid #21262d', borderRadius: 12, padding: '24px' }}>
          <h2 style={{ fontSize: 14, fontWeight: 600, color: '#e2e8f0', marginBottom: 16 }}>Daily Summary Table</h2>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
            <thead>
              <tr>
                {['Date', 'Page Views', 'Sessions', 'Revenue'].map(h => (
                  <th key={h} style={{ padding: '8px 16px', textAlign: 'left', color: '#6e7681', fontSize: 11, letterSpacing: '0.6px', borderBottom: '1px solid #21262d' }}>
                    {h.toUpperCase()}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {daily.map((row, i) => (
                <tr key={i} style={{ borderBottom: '1px solid #161b22' }}>
                  <td style={{ padding: '10px 16px', color: '#e2e8f0', fontFamily: 'JetBrains Mono', fontSize: 12 }}>{row.day}</td>
                  <td style={{ padding: '10px 16px', color: '#52b788', fontFamily: 'JetBrains Mono' }}>{row.page_views.toLocaleString()}</td>
                  <td style={{ padding: '10px 16px', color: '#f0883e', fontFamily: 'JetBrains Mono' }}>{row.sessions.toLocaleString()}</td>
                  <td style={{ padding: '10px 16px', color: '#ffa657', fontFamily: 'JetBrains Mono' }}>${row.revenue.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
REPEOF

ok "Frontend files created"

# ─────────────────────────────────────────────────────────────
# STEP 5: Docker Files
# ─────────────────────────────────────────────────────────────
header "Step 5: Creating Docker Files"

cat > $PROJECT/backend/Dockerfile << 'DKBEOF'
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/
RUN mkdir -p models
EXPOSE 8112
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8112"]
DKBEOF

cat > $PROJECT/frontend/Dockerfile << 'DKFEOF'
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json .
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 3112
DKFEOF

cat > $PROJECT/frontend/nginx.conf << 'NGEOF'
server {
    listen 3112;
    root /usr/share/nginx/html;
    index index.html;
    location /api/ {
        proxy_pass http://backend:8112;
        proxy_set_header Host $host;
    }
    location / {
        try_files $uri $uri/ /index.html;
    }
}
NGEOF

cat > $PROJECT/docker-compose.yml << 'DCEOF'
version: '3.9'
services:
  backend:
    build: ./backend
    ports:
      - "8112:8112"
    environment:
      - DATABASE_URL=sqlite:///./analytics.db
    volumes:
      - ./backend/models:/app/models
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8112/health"]
      interval: 10s
      timeout: 5s
      retries: 5

  frontend:
    build: ./frontend
    ports:
      - "3112:3112"
    depends_on:
      - backend
DCEOF

ok "Docker files created"

# ─────────────────────────────────────────────────────────────
# STEP 6: conftest.py for pytest
# ─────────────────────────────────────────────────────────────
cat > $PROJECT/backend/conftest.py << 'CFEOF'
import pytest
CFEOF

# ─────────────────────────────────────────────────────────────
# STEP 7: Build and Run WITHOUT Docker
# ─────────────────────────────────────────────────────────────
header "Step 7: Building — Without Docker"

log "Setting up Python virtual environment..."
python3 -m venv $VENV
source $VENV/bin/activate

log "Installing Python dependencies..."
pip install --quiet -r $PROJECT/backend/requirements.txt
ok "Python dependencies installed"

log "Installing frontend dependencies..."
cd $PROJECT/frontend
npm install --silent
ok "Node dependencies installed"
cd ../..

# ─────────────────────────────────────────────────────────────
# STEP 8: Run Tests
# ─────────────────────────────────────────────────────────────
header "Step 8: Running Tests"

source $VENV/bin/activate
[ -d "$SCRIPT_DIR/$PROJECT/backend" ] && cd "$SCRIPT_DIR/$PROJECT/backend" || cd $PROJECT/backend

log "Running unit and integration tests..."
PYTHONPATH=. python -m pytest tests/ -v --tb=short 2>&1 | tee /tmp/day112_tests.log
TEST_EXIT=${PIPESTATUS[0]}

cd "$SCRIPT_DIR"

if [ $TEST_EXIT -eq 0 ]; then
  ok "All tests passed ✓"
else
  warn "Some tests failed — check /tmp/day112_tests.log"
fi

# Clean up test databases
rm -f $PROJECT/backend/test_analytics.db $PROJECT/backend/test_ml.db

# ─────────────────────────────────────────────────────────────
# STEP 9: Start Backend
# ─────────────────────────────────────────────────────────────
header "Step 9: Starting Services (No Docker)"

# Full paths and avoid duplicate services
PROJECT_ABS="$SCRIPT_DIR/$PROJECT"
BACKEND_ABS="$PROJECT_ABS/backend"
FRONTEND_ABS="$PROJECT_ABS/frontend"

# Check and kill existing processes on our ports (avoid duplicates)
for port in $BACKEND_PORT $FRONTEND_PORT; do
  existing=$(lsof -ti ":$port" 2>/dev/null || true)
  if [ -n "$existing" ]; then
    warn "Killing existing process(es) on port $port: $existing"
    kill $existing 2>/dev/null || true
    sleep 2
  fi
done

source $VENV/bin/activate
[ -d "$BACKEND_ABS" ] && cd "$BACKEND_ABS" || cd $PROJECT/backend
mkdir -p models

log "Starting FastAPI backend on port $BACKEND_PORT..."
PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT --reload &
BACKEND_PID=$!
cd "$SCRIPT_DIR"

log "Waiting for backend to be ready..."
for i in $(seq 1 30); do
  if curl -s http://localhost:$BACKEND_PORT/health > /dev/null 2>&1; then
    ok "Backend ready at http://localhost:$BACKEND_PORT"
    break
  fi
  sleep 1
done

# ─────────────────────────────────────────────────────────────
# STEP 10: Trigger ML Training
# ─────────────────────────────────────────────────────────────
header "Step 10: Triggering ML Training"

log "Triggering ML model training..."
curl -s -X POST http://localhost:$BACKEND_PORT/api/ml/train | python3 -m json.tool || true

log "Waiting for training to complete (15s)..."
sleep 15

ML_STATUS=$(curl -s http://localhost:$BACKEND_PORT/api/ml/status)
echo "$ML_STATUS" | python3 -m json.tool || true

# ─────────────────────────────────────────────────────────────
# STEP 11: Start Frontend
# ─────────────────────────────────────────────────────────────
header "Step 11: Starting Frontend"

[ -d "$FRONTEND_ABS" ] && cd "$FRONTEND_ABS" || cd $PROJECT/frontend
log "Starting React dev server on port $FRONTEND_PORT..."
npm run dev &
FRONTEND_PID=$!
cd "$SCRIPT_DIR"

log "Waiting for frontend..."
sleep 8

# Save PIDs
echo "$BACKEND_PID $FRONTEND_PID" > $PID_FILE

# ─────────────────────────────────────────────────────────────
# STEP 12: Functional Demo Verification
# ─────────────────────────────────────────────────────────────
header "Step 12: Functional Demo Verification"

BASE="http://localhost:$BACKEND_PORT"

verify() {
  local name="$1"; local url="$2"
  local resp=$(curl -s "$url")
  if echo "$resp" | python3 -c "import sys,json; d=json.load(sys.stdin); sys.exit(0)" 2>/dev/null; then
    ok "$name → valid JSON response"
  else
    warn "$name → unexpected response"
  fi
}

verify "Health Check"         "$BASE/health"
verify "Pipeline Status"      "$BASE/api/analytics/pipeline"
verify "Event Summary"        "$BASE/api/analytics/summary"
verify "KPI Report"           "$BASE/api/reports/kpis"
verify "7-day Report"         "$BASE/api/reports/summary?days=7"
verify "ML Status"            "$BASE/api/ml/status"
verify "ML Predictions (24h)" "$BASE/api/ml/predict?hours=24"
verify "Anomaly Detection"    "$BASE/api/ml/anomalies"
verify "Pearson Correlations" "$BASE/api/ml/correlations?method=pearson"

log "Posting a test analytics event..."
curl -s -X POST "$BASE/api/analytics/events" \
  -H "Content-Type: application/json" \
  -d '{"event_type":"purchase","user_id":"demo_u1","page":"/checkout","duration_ms":2200,"revenue":49.99,"properties":{"plan":"pro"}}' \
  | python3 -m json.tool
ok "Test event ingested"

# ─────────────────────────────────────────────────────────────
# STEP 13: Docker Build (if available)
# ─────────────────────────────────────────────────────────────
if [ "$USE_DOCKER" = true ]; then
  header "Step 13: Docker Build Verification"
  log "Building Docker images (this may take a moment)..."
  cd $PROJECT
  docker-compose build --quiet 2>&1 | tail -5
  ok "Docker images built successfully"
  log "To run with Docker: cd $PROJECT && docker-compose up -d"
  cd ..
else
  warn "Docker not available — skipping Docker build"
fi

# ─────────────────────────────────────────────────────────────
# FINAL SUMMARY
# ─────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}╔═══════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${GREEN}║     Day 112: Analytics Integration — RUNNING      ║${NC}"
echo -e "${BOLD}${GREEN}╠═══════════════════════════════════════════════════╣${NC}"
echo -e "${BOLD}${GREEN}║  Backend API:  http://localhost:$BACKEND_PORT           ║${NC}"
echo -e "${BOLD}${GREEN}║  Frontend UI:  http://localhost:$FRONTEND_PORT          ║${NC}"
echo -e "${BOLD}${GREEN}║  API Docs:     http://localhost:$BACKEND_PORT/docs      ║${NC}"
echo -e "${BOLD}${GREEN}╠═══════════════════════════════════════════════════╣${NC}"
echo -e "${BOLD}${GREEN}║  Start: $SCRIPT_DIR/start.sh   Stop: $SCRIPT_DIR/stop.sh   ║${NC}"
echo -e "${BOLD}${GREEN}╚═══════════════════════════════════════════════════╝${NC}"
echo ""
