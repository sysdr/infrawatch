import numpy as np
import pandas as pd
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class ModelEvaluator:
    def __init__(self, anomaly_detector, predictive_analytics, pattern_recognizer):
        self.anomaly_detector = anomaly_detector
        self.predictive_analytics = predictive_analytics
        self.pattern_recognizer = pattern_recognizer

    def evaluate(self, df: pd.DataFrame) -> dict:
        results = {
            "anomaly_model": {},
            "forecast_model": {},
            "pattern_model": {},
            "overall_health": True
        }

        if self.anomaly_detector.is_trained:
            try:
                batch = self.anomaly_detector.batch_score(df)
                scores = [b["anomaly_score"] for b in batch]
                anomalies = [b["is_anomaly"] for b in batch]
                anomaly_rate = float(np.mean(anomalies))
                drift = self.anomaly_detector.compute_drift(df)
                results["anomaly_model"] = {
                    "status": "trained",
                    "training_samples": len(df),
                    "anomaly_rate": round(anomaly_rate, 4),
                    "avg_anomaly_score": round(float(np.mean(scores)), 4),
                    "min_score": round(float(np.min(scores)), 4),
                    "max_score": round(float(np.max(scores)), 4),
                    "drift_score": round(drift, 4),
                    "is_healthy": anomaly_rate < 0.15 and drift < 0.3
                }
            except Exception as e:
                results["anomaly_model"] = {"status": "error", "error": str(e)}

        if self.predictive_analytics.is_trained:
            try:
                rmse_values = {}
                for metric, fitted in self.predictive_analytics.fitted.items():
                    history = self.predictive_analytics.training_history.get(metric)
                    if history is not None and len(history) > 0:
                        in_sample = fitted.fittedvalues
                        actual_arr = np.asarray(history.values)
                        pred_arr = np.asarray(in_sample.values)
                        n = min(len(actual_arr), len(pred_arr))
                        if n > 0:
                            actual = actual_arr[-n:]
                            pred = pred_arr[-n:]
                            rmse = float(np.sqrt(np.mean((actual - pred) ** 2)))
                            rmse_values[metric] = round(rmse, 4)
                avg_rmse = float(np.mean(list(rmse_values.values()))) if rmse_values else 999.0
                results["forecast_model"] = {
                    "status": "trained",
                    "trained_metrics": list(rmse_values.keys()),
                    "rmse_per_metric": rmse_values,
                    "avg_rmse": round(avg_rmse, 4),
                    "is_healthy": avg_rmse < 20.0
                }
            except Exception as e:
                results["forecast_model"] = {"status": "error", "error": str(e)}

        if self.pattern_recognizer.is_trained:
            results["pattern_model"] = {
                "status": "trained",
                "n_clusters": self.pattern_recognizer.n_clusters,
                "silhouette_score": round(self.pattern_recognizer.silhouette, 4),
                "cluster_profiles": self.pattern_recognizer.cluster_profiles,
                "is_healthy": self.pattern_recognizer.silhouette > 0.15
            }

        ad_health = results["anomaly_model"].get("is_healthy", False)
        fc_health = results["forecast_model"].get("is_healthy", False)
        pt_health = results["pattern_model"].get("is_healthy", False)
        results["overall_health"] = ad_health and fc_health and pt_health
        return results
