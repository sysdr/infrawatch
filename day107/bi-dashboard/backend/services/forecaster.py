import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from models.kpi import KPIMetric, KPIValue, Forecast
from sklearn.metrics import mean_absolute_error, mean_squared_error

class Forecaster:
    def __init__(self, db: Session):
        self.db = db

    def forecast_metric(self, metric_name: str, forecast_days: int = 7, model_type: str = "arima") -> Dict:
        metric = self.db.query(KPIMetric).filter(KPIMetric.name == metric_name).first()
        if not metric:
            raise ValueError(f"Metric {metric_name} not found")
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=90)
        values = self.db.query(KPIValue).filter(
            KPIValue.metric_id == metric.id,
            KPIValue.timestamp >= start_date,
            KPIValue.timestamp <= end_date
        ).order_by(KPIValue.timestamp).all()
        if len(values) < 14:
            return {"status": "insufficient_data", "message": "Need at least 14 days of data for forecasting"}
        df = pd.DataFrame([{"timestamp": v.timestamp, "value": v.value} for v in values])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp').set_index('timestamp')
        daily_data = df['value'].resample('D').mean().ffill()
        if len(daily_data) < 14:
            return {"status": "insufficient_data", "message": "Need at least 14 days of data for forecasting"}
        train_size = max(int(len(daily_data) * 0.8), 7)
        train_data = daily_data[:train_size]
        test_data = daily_data[train_size:]
        forecast_result = self._simple_forecast(train_data, forecast_days)
        base_date = datetime.utcnow()
        for i, (pred, lower, upper) in enumerate(zip(
            forecast_result['predictions'],
            forecast_result['confidence_lower'],
            forecast_result['confidence_upper']
        )):
            forecast_date = base_date + timedelta(days=i+1)
            self.db.add(Forecast(
                metric_id=metric.id, forecast_date=forecast_date,
                predicted_value=float(pred), confidence_lower=float(lower), confidence_upper=float(upper),
                model_type=model_type, model_parameters=forecast_result.get('model_params', {}),
                accuracy_metrics=forecast_result.get('accuracy_metrics', {})
            ))
        self.db.commit()
        return {
            "metric_name": metric_name, "model_type": model_type, "forecast_days": forecast_days,
            "predictions": [
                {"date": (base_date + timedelta(days=i+1)).isoformat(), "predicted_value": float(pred),
                 "confidence_lower": float(lower), "confidence_upper": float(upper)}
                for i, (pred, lower, upper) in enumerate(zip(
                    forecast_result['predictions'], forecast_result['confidence_lower'], forecast_result['confidence_upper']
                ))
            ],
            "accuracy_metrics": forecast_result.get('accuracy_metrics', {})
        }

    def _simple_forecast(self, data: pd.Series, forecast_steps: int) -> Dict:
        last_value = data.iloc[-1]
        trend = (data.iloc[-1] - data.iloc[-7]) / 7 if len(data) > 7 else 0
        predictions = np.array([last_value + (trend * (i + 1)) for i in range(forecast_steps)])
        std_error = data.std() if data.std() > 0 else 1.0
        return {
            "predictions": predictions,
            "confidence_lower": predictions - 1.96 * std_error,
            "confidence_upper": predictions + 1.96 * std_error,
            "model_params": {"method": "simple_moving_average"},
            "accuracy_metrics": {}
        }
