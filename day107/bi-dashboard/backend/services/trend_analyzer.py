import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from models.kpi import KPIMetric, KPIValue, TrendAnalysis

class TrendAnalyzer:
    def __init__(self, db: Session):
        self.db = db

    def analyze_trend(self, metric_name: str, window_days: int = 30, anomaly_threshold: float = 2.0) -> Dict:
        metric = self.db.query(KPIMetric).filter(KPIMetric.name == metric_name).first()
        if not metric:
            raise ValueError(f"Metric {metric_name} not found")
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=window_days)
        values = self.db.query(KPIValue).filter(
            KPIValue.metric_id == metric.id,
            KPIValue.timestamp >= start_date,
            KPIValue.timestamp <= end_date
        ).order_by(KPIValue.timestamp).all()
        if len(values) < 7:
            return {"status": "insufficient_data", "message": "Need at least 7 data points for trend analysis"}
        df = pd.DataFrame([{"timestamp": v.timestamp, "value": v.value} for v in values])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp').set_index('timestamp')
        ma_7d = df['value'].rolling(window=7, min_periods=1).mean()
        ma_30d = df['value'].rolling(window=30, min_periods=1).mean()
        std_dev_raw = df['value'].std()
        std_dev = float(std_dev_raw) if pd.notna(std_dev_raw) and std_dev_raw > 0 else 0.0
        mean_value = float(df['value'].mean())
        current_value = float(df['value'].iloc[-1])
        z_score = (current_value - mean_value) / std_dev if std_dev > 0 else 0.0
        z_score = float(z_score) if not np.isnan(z_score) else 0.0
        is_anomaly = abs(z_score) > anomaly_threshold
        trend_result = self._mann_kendall_test(df['value'].values)
        trend_direction = "stable"
        trend_strength = 0.0
        p_val = trend_result.get('p_value') or 1.0
        if p_val < 0.05:
            tau = trend_result.get('tau') or 0
            if tau > 0:
                trend_direction, trend_strength = "up", min(abs(tau), 1.0)
            elif tau < 0:
                trend_direction, trend_strength = "down", min(abs(tau), 1.0)
        confidence = float(1 - p_val) if not np.isnan(p_val) else 0.0
        ma_7_val = ma_7d.iloc[-1] if len(ma_7d) > 0 else None
        ma_30_val = ma_30d.iloc[-1] if len(ma_30d) > 0 else None
        def _no_nan(v):
            if v is None: return None
            if isinstance(v, (int, float)) and (np.isnan(v) or np.isinf(v)):
                return None
            return v
        meta = {
            "mann_kendall_tau": _no_nan(trend_result.get('tau')),
            "mann_kendall_p_value": _no_nan(trend_result.get('p_value')),
            "data_points": len(df),
            "window_days": window_days
        }
        analysis = TrendAnalysis(
            metric_id=metric.id, analysis_date=datetime.utcnow(),
            trend_direction=trend_direction, trend_strength=trend_strength,
            moving_average_7d=float(ma_7_val) if ma_7_val is not None and not np.isnan(ma_7_val) else None,
            moving_average_30d=float(ma_30_val) if ma_30_val is not None and not np.isnan(ma_30_val) else None,
            standard_deviation=std_dev, z_score=z_score, is_anomaly=int(is_anomaly),
            confidence_level=confidence,
            analysis_metadata=meta
        )
        self.db.add(analysis)
        self.db.commit()
        return {
            "metric_name": metric_name, "trend_direction": trend_direction, "trend_strength": trend_strength,
            "is_anomaly": is_anomaly, "z_score": z_score, "current_value": current_value,
            "mean_value": mean_value, "std_deviation": std_dev,
            "ma_7d": float(ma_7_val) if ma_7_val is not None and not np.isnan(ma_7_val) else None,
            "ma_30d": float(ma_30_val) if ma_30_val is not None and not np.isnan(ma_30_val) else None,
            "confidence_level": confidence, "mann_kendall_tau": trend_result.get('tau'), "data_points": len(df)
        }

    def _mann_kendall_test(self, data: np.ndarray) -> Dict:
        n = len(data)
        if n < 2:
            return {"tau": 0.0, "p_value": 1.0, "z_statistic": 0.0}
        s = sum(np.sign(data[j] - data[i]) for i in range(n - 1) for j in range(i + 1, n))
        unique_data = np.unique(data)
        g = len(unique_data)
        if n == g:
            var_s = (n * (n - 1) * (2 * n + 5)) / 18
        else:
            tp = np.array([np.sum(data == u) for u in unique_data])
            var_s = (n * (n - 1) * (2 * n + 5) - np.sum(tp * (tp - 1) * (2 * tp + 5))) / 18
        if var_s <= 0:
            return {"tau": 0.0, "p_value": 1.0, "z_statistic": 0.0}
        z = (s - 1) / np.sqrt(var_s) if s > 0 else ((s + 1) / np.sqrt(var_s) if s < 0 else 0)
        z = float(z)
        if np.isnan(z) or np.isinf(z):
            z = 0.0
        p_value = 2 * (1 - stats.norm.cdf(abs(z)))
        p_value = float(p_value) if not np.isnan(p_value) else 1.0
        denom = 0.5 * n * (n - 1)
        tau = (s / denom) if denom else 0.0
        tau = float(tau) if not np.isnan(tau) else 0.0
        return {"tau": tau, "p_value": p_value, "z_statistic": z}

    def detect_anomalies(self, metric_name: str, threshold: float = 2.5) -> List[Dict]:
        analysis = self.analyze_trend(metric_name, anomaly_threshold=threshold)
        if analysis.get("status") == "insufficient_data":
            return []
        if analysis["is_anomaly"]:
            return [{"timestamp": datetime.utcnow().isoformat(), "metric_name": metric_name, "value": analysis["current_value"], "z_score": analysis["z_score"], "severity": "high" if abs(analysis["z_score"]) > 3 else "medium"}]
        return []
