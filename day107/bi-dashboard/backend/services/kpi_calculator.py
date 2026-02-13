import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from models.kpi import KPIMetric, KPIValue, TrendAnalysis

class KPICalculator:
    """Calculate and aggregate KPIs from raw data"""

    def __init__(self, db: Session):
        self.db = db

    def calculate_kpi(
        self,
        metric_name: str,
        start_date: datetime,
        end_date: datetime,
        dimensions: Optional[Dict] = None
    ) -> Dict:
        """Calculate KPI with trend information"""

        metric = self.db.query(KPIMetric).filter(
            KPIMetric.name == metric_name
        ).first()

        if not metric:
            raise ValueError(f"Metric {metric_name} not found")

        query = self.db.query(KPIValue).filter(
            KPIValue.metric_id == metric.id,
            KPIValue.timestamp >= start_date,
            KPIValue.timestamp <= end_date
        )

        if dimensions:
            for key, value in dimensions.items():
                query = query.filter(
                    KPIValue.dimensions[key].astext == value
                )

        values = query.order_by(KPIValue.timestamp).all()

        if not values:
            return {
                "metric_name": metric_name,
                "display_name": metric.display_name,
                "current_value": None,
                "previous_value": None,
                "change_percentage": None,
                "trend": "unknown",
                "unit": metric.unit,
                "target_value": metric.target_value,
                "data_points": 0,
                "period_start": start_date.isoformat(),
                "period_end": end_date.isoformat()
            }

        df = pd.DataFrame([
            {"timestamp": v.timestamp, "value": v.value}
            for v in values
        ])

        current_value = df['value'].iloc[-1] if len(df) > 0 else None

        previous_value = None
        if len(df) > 1:
            period_length = (end_date - start_date).days
            previous_start = start_date - timedelta(days=period_length)
            prev_query = self.db.query(KPIValue).filter(
                KPIValue.metric_id == metric.id,
                KPIValue.timestamp >= previous_start,
                KPIValue.timestamp < start_date
            )
            prev_values = prev_query.all()
            if prev_values:
                prev_df = pd.DataFrame([{"value": v.value} for v in prev_values])
                previous_value = prev_df['value'].mean()

        change_percentage = None
        trend = "stable"
        if previous_value and previous_value != 0:
            change_percentage = ((current_value - previous_value) / previous_value) * 100
            if abs(change_percentage) > 5:
                trend = "up" if change_percentage > 0 else "down"

        return {
            "metric_name": metric_name,
            "display_name": metric.display_name,
            "current_value": float(current_value) if current_value else None,
            "previous_value": float(previous_value) if previous_value else None,
            "change_percentage": float(change_percentage) if change_percentage else None,
            "trend": trend,
            "unit": metric.unit,
            "target_value": metric.target_value,
            "data_points": len(df),
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat()
        }

    def get_dashboard_kpis(self) -> List[Dict]:
        metrics = self.db.query(KPIMetric).all()
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        kpis = []
        for metric in metrics:
            try:
                kpi_data = self.calculate_kpi(metric.name, start_date, end_date)
                kpis.append(kpi_data)
            except Exception as e:
                print(f"Error calculating KPI {metric.name}: {e}")
                continue
        return kpis

    def get_sparkline_data(self, metric_name: str, days: int = 7) -> List[Dict]:
        metric = self.db.query(KPIMetric).filter(KPIMetric.name == metric_name).first()
        if not metric:
            return []
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        values = self.db.query(KPIValue).filter(
            KPIValue.metric_id == metric.id,
            KPIValue.timestamp >= start_date,
            KPIValue.timestamp <= end_date
        ).order_by(KPIValue.timestamp).all()
        return [{"timestamp": v.timestamp.isoformat(), "value": float(v.value)} for v in values]
