import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
import warnings
import logging
from typing import Optional

warnings.filterwarnings("ignore")
logger = logging.getLogger(__name__)

FORECASTABLE_METRICS = ["cpu_usage", "memory_usage", "request_rate", "error_rate", "latency_p99"]

class PredictiveAnalytics:
    def __init__(self, forecast_steps: int = 24):
        self.forecast_steps = forecast_steps
        self.models: dict = {}
        self.fitted: dict = {}
        self.is_trained: bool = False
        self.training_history: dict = {}

    def _determine_order(self, series: pd.Series) -> tuple:
        result = adfuller(series.dropna())
        d = 0 if result[1] < 0.05 else 1
        return (2, d, 2)

    def train(self, df: pd.DataFrame) -> dict:
        metrics_results = {}
        for metric in FORECASTABLE_METRICS:
            try:
                series = df[metric].dropna()
                if len(series) < 20:
                    continue
                order = self._determine_order(series)
                model = ARIMA(series, order=order)
                fitted = model.fit(method_kwargs={"warn_convergence": False})
                self.models[metric] = model
                self.fitted[metric] = fitted
                self.training_history[metric] = series.copy()

                predictions = fitted.fittedvalues
                rmse = float(np.sqrt(np.mean((series.values - predictions.values) ** 2)))
                metrics_results[metric] = {"rmse": rmse, "order": order, "samples": len(series)}
            except Exception as e:
                logger.warning(f"ARIMA training failed for {metric}: {e}")
                metrics_results[metric] = {"error": str(e)}

        self.is_trained = len(self.fitted) > 0
        return metrics_results

    def forecast(self, metric: str = "cpu_usage") -> dict:
        if metric not in self.fitted:
            raise ValueError(f"No trained model for metric: {metric}")
        fitted_model = self.fitted[metric]
        forecast_result = fitted_model.get_forecast(steps=self.forecast_steps)
        point_forecast = forecast_result.predicted_mean
        conf_int = forecast_result.conf_int()

        timestamps = [f"T+{i+1}h" for i in range(self.forecast_steps)]

        return {
            "metric_name": metric,
            "timestamps": timestamps,
            "forecast": [round(float(v), 3) for v in point_forecast.values],
            "lower_bound": [round(float(v), 3) for v in conf_int.iloc[:, 0].values],
            "upper_bound": [round(float(v), 3) for v in conf_int.iloc[:, 1].values],
        }

    def forecast_all(self) -> dict:
        results = {}
        for metric in self.fitted:
            try:
                results[metric] = self.forecast(metric)
            except Exception as e:
                logger.warning(f"Forecast failed for {metric}: {e}")
        return results

    def compute_rmse(self, metric: str, actual: pd.Series) -> float:
        if metric not in self.fitted:
            return 999.0
        fitted_model = self.fitted[metric]
        forecast = fitted_model.get_forecast(steps=len(actual))
        predicted = forecast.predicted_mean.values
        actual_vals = actual.values[:len(predicted)]
        return float(np.sqrt(np.mean((actual_vals - predicted) ** 2)))
