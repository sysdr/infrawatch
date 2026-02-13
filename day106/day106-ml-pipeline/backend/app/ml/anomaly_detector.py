import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import RobustScaler
from sklearn.decomposition import PCA
from scipy.stats import ks_2samp
import logging
from typing import Optional

logger = logging.getLogger(__name__)

FEATURE_COLS = ["cpu_usage", "memory_usage", "request_rate",
                "error_rate", "latency_p99", "disk_io", "network_in", "network_out"]

class AnomalyDetector:
    def __init__(self, contamination: float = 0.05):
        self.contamination = contamination
        self.model: Optional[IsolationForest] = None
        self.scaler = RobustScaler()
        self.pca = PCA(n_components=2)
        self.is_trained = False
        self.training_data: Optional[np.ndarray] = None
        self.feature_means: Optional[dict] = None

    def train(self, df: pd.DataFrame) -> dict:
        data = df[FEATURE_COLS].values
        scaled = self.scaler.fit_transform(data)
        self.model = IsolationForest(
            contamination=self.contamination,
            n_estimators=200,
            max_samples="auto",
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(scaled)
        self.pca.fit(scaled)
        self.training_data = scaled.copy()
        self.feature_means = df[FEATURE_COLS].mean().to_dict()
        self.is_trained = True
        scores = self.model.score_samples(scaled)
        labels = self.model.predict(scaled)
        return {
            "training_samples": len(data),
            "anomaly_rate": float((labels == -1).mean()),
            "mean_score": float(scores.mean()),
            "contamination": self.contamination
        }

    def score(self, df: pd.DataFrame) -> dict:
        if not self.is_trained:
            raise RuntimeError("Model not trained. Call train() first.")
        data = df[FEATURE_COLS].values
        scaled = self.scaler.transform(data)
        scores = self.model.score_samples(scaled)
        labels = self.model.predict(scaled)
        anomaly_mask = labels == -1
        pca_coords = self.pca.transform(scaled)

        affected = []
        if anomaly_mask.any():
            row = df[FEATURE_COLS].iloc[-1]
            means = pd.Series(self.feature_means)
            deviations = ((row - means) / (means + 1e-6)).abs()
            affected = deviations.nlargest(3).index.tolist()

        severity = "none"
        score_val = float(scores[-1])
        if score_val < -0.5:
            severity = "critical"
        elif score_val < -0.4:
            severity = "high"
        elif score_val < -0.3:
            severity = "medium"
        elif bool(anomaly_mask[-1]):
            severity = "low"

        return {
            "anomaly_score": score_val,
            "is_anomaly": bool(anomaly_mask[-1]),
            "severity": severity,
            "affected_metrics": affected,
            "pca_x": float(pca_coords[-1, 0]),
            "pca_y": float(pca_coords[-1, 1]),
            "description": self._describe(severity, affected)
        }

    def batch_score(self, df: pd.DataFrame) -> list:
        if not self.is_trained:
            raise RuntimeError("Model not trained.")
        data = df[FEATURE_COLS].values
        scaled = self.scaler.transform(data)
        scores = self.model.score_samples(scaled)
        labels = self.model.predict(scaled)
        pca_coords = self.pca.transform(scaled)
        results = []
        for i in range(len(df)):
            results.append({
                "anomaly_score": float(scores[i]),
                "is_anomaly": bool(labels[i] == -1),
                "pca_x": float(pca_coords[i, 0]),
                "pca_y": float(pca_coords[i, 1])
            })
        return results

    def compute_drift(self, new_df: pd.DataFrame) -> float:
        if self.training_data is None:
            return 0.0
        new_scaled = self.scaler.transform(new_df[FEATURE_COLS].values)
        ks_stats = []
        for col_idx in range(self.training_data.shape[1]):
            stat, _ = ks_2samp(self.training_data[:, col_idx], new_scaled[:, col_idx])
            ks_stats.append(stat)
        return float(np.mean(ks_stats))

    def _describe(self, severity: str, affected: list) -> str:
        if severity == "none":
            return "System operating within normal parameters"
        metrics = ", ".join(affected) if affected else "multiple metrics"
        descriptions = {
            "critical": f"Critical anomaly detected: {metrics} showing extreme deviation",
            "high": f"High severity anomaly: {metrics} significantly outside baseline",
            "medium": f"Moderate anomaly: {metrics} showing unusual behavior",
            "low": f"Minor anomaly detected in {metrics}"
        }
        return descriptions.get(severity, "Anomaly detected")
