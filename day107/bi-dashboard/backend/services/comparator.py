import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy.orm import Session
from scipy import stats
from models.kpi import KPIMetric, KPIValue

def _safe_float(x: Any) -> float:
    if x is None or (isinstance(x, float) and (np.isnan(x) or np.isinf(x))):
        return 0.0
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0

def _get_dimensions(value: KPIValue) -> dict:
    d = value.dimensions
    if d is None:
        return {}
    if isinstance(d, dict):
        return d
    if isinstance(d, str):
        try:
            return json.loads(d)
        except (json.JSONDecodeError, TypeError):
            return {}
    return {}

class MetricComparator:
    def __init__(self, db: Session):
        self.db = db

    def compare_by_dimension(self, metric_name: str, dimension: str, period_days: int = 30) -> Dict:
        metric = self.db.query(KPIMetric).filter(KPIMetric.name == metric_name).first()
        if not metric:
            raise ValueError(f"Metric {metric_name} not found")
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=period_days)
        values = self.db.query(KPIValue).filter(
            KPIValue.metric_id == metric.id,
            KPIValue.timestamp >= start_date,
            KPIValue.timestamp <= end_date
        ).all()
        dimension_groups = {}
        for value in values:
            dims = _get_dimensions(value)
            if dimension in dims:
                dim_value = dims[dimension]
                dimension_groups.setdefault(dim_value, []).append(value.value)
        if not values:
            return {"metric_name": metric_name, "dimension": dimension, "period_days": period_days, "overall_mean": 0.0, "comparisons": []}
        overall_mean = float(np.mean([v.value for v in values]))
        comparisons = []
        for dim_value, group_values in dimension_groups.items():
            if not group_values:
                continue
            group_mean = float(np.mean(group_values))
            std_g = float(np.std(group_values)) if len(group_values) > 1 else 0.0
            try:
                _, p_value = stats.ttest_1samp(group_values, overall_mean)
                p_value = _safe_float(p_value)
                if np.isnan(p_value):
                    p_value = 1.0
            except Exception:
                p_value = 1.0
            vs_overall = ((group_mean - overall_mean) / overall_mean * 100) if overall_mean else 0.0
            comparisons.append({
                "dimension_value": dim_value, "mean": group_mean, "std_dev": std_g,
                "count": len(group_values), "vs_overall": _safe_float(vs_overall),
                "p_value": p_value, "significant": p_value < 0.05
            })
        comparisons.sort(key=lambda x: x['mean'], reverse=True)
        return {"metric_name": metric_name, "dimension": dimension, "period_days": period_days, "overall_mean": overall_mean, "comparisons": comparisons}

    def compare_time_periods(self, metric_name: str, period1_start: datetime, period1_end: datetime, period2_start: datetime, period2_end: datetime) -> Dict:
        metric = self.db.query(KPIMetric).filter(KPIMetric.name == metric_name).first()
        if not metric:
            raise ValueError(f"Metric {metric_name} not found")
        period1_values = self.db.query(KPIValue).filter(KPIValue.metric_id == metric.id, KPIValue.timestamp >= period1_start, KPIValue.timestamp <= period1_end).all()
        period2_values = self.db.query(KPIValue).filter(KPIValue.metric_id == metric.id, KPIValue.timestamp >= period2_start, KPIValue.timestamp <= period2_end).all()
        if not period1_values or not period2_values:
            return {"status": "insufficient_data", "message": "Need data for both periods"}
        p1_data = [v.value for v in period1_values]
        p2_data = [v.value for v in period2_values]
        p1_mean = float(np.mean(p1_data))
        p2_mean = float(np.mean(p2_data))
        std1 = float(np.std(p1_data)) if len(p1_data) > 1 else 0.0
        std2 = float(np.std(p2_data)) if len(p2_data) > 1 else 0.0
        try:
            _, p_value = stats.ttest_ind(p1_data, p2_data)
            p_value = _safe_float(p_value)
            if np.isnan(p_value):
                p_value = 1.0
        except Exception:
            p_value = 1.0
        change_pct = ((p2_mean - p1_mean) / p1_mean * 100) if p1_mean != 0 else 0.0
        return {
            "metric_name": metric_name,
            "period1": {"start": period1_start.isoformat(), "end": period1_end.isoformat(), "mean": p1_mean, "std": std1, "count": len(p1_data)},
            "period2": {"start": period2_start.isoformat(), "end": period2_end.isoformat(), "mean": p2_mean, "std": std2, "count": len(p2_data)},
            "comparison": {"change_percentage": _safe_float(change_pct), "absolute_change": _safe_float(p2_mean - p1_mean), "p_value": p_value, "statistically_significant": p_value < 0.05}
        }
