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
