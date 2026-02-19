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
