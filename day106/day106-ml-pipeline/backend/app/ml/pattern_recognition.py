import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
import logging
from typing import Optional

logger = logging.getLogger(__name__)

FEATURE_COLS = ["cpu_usage", "memory_usage", "request_rate", "error_rate", "latency_p99"]

class PatternRecognizer:
    def __init__(self, n_clusters: int = 3):
        self.n_clusters = n_clusters
        self.model: Optional[KMeans] = None
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=2)
        self.is_trained = False
        self.cluster_profiles: dict = {}
        self.silhouette: float = 0.0

    def fit(self, df: pd.DataFrame) -> dict:
        data = df[FEATURE_COLS].values
        scaled = self.scaler.fit_transform(data)
        self.model = KMeans(
            n_clusters=self.n_clusters,
            n_init=20,
            max_iter=500,
            random_state=42
        )
        labels = self.model.fit_predict(scaled)
        pca_coords = self.pca.fit_transform(scaled)
        self.is_trained = True

        if len(set(labels)) > 1:
            self.silhouette = float(silhouette_score(scaled, labels))
        else:
            self.silhouette = 0.0

        df_labeled = df[FEATURE_COLS].copy()
        df_labeled["cluster_id"] = labels
        df_labeled["pca_x"] = pca_coords[:, 0]
        df_labeled["pca_y"] = pca_coords[:, 1]

        self.cluster_profiles = {}
        results = []
        for cluster_id in range(self.n_clusters):
            mask = labels == cluster_id
            cluster_data = df_labeled[mask]
            profile = cluster_data[FEATURE_COLS].mean().to_dict()
            cluster_label = self._assign_label(profile)
            self.cluster_profiles[cluster_id] = {
                "label": cluster_label,
                "profile": profile,
                "count": int(mask.sum())
            }
            results.append({
                "cluster_id": cluster_id,
                "cluster_label": cluster_label,
                "sample_count": int(mask.sum()),
                "silhouette_score": self.silhouette,
                "centroid": {k: round(v, 3) for k, v in profile.items()}
            })
        return {"clusters": results, "silhouette_score": self.silhouette}

    def predict(self, df: pd.DataFrame) -> list:
        if not self.is_trained:
            raise RuntimeError("Model not trained.")
        data = df[FEATURE_COLS].values
        scaled = self.scaler.transform(data)
        labels = self.model.predict(scaled)
        pca_coords = self.pca.transform(scaled)
        results = []
        for i, label in enumerate(labels):
            profile = self.cluster_profiles.get(label, {})
            results.append({
                "index": i,
                "cluster_id": int(label),
                "cluster_label": profile.get("label", f"Cluster {label}"),
                "pca_x": float(pca_coords[i, 0]),
                "pca_y": float(pca_coords[i, 1])
            })
        return results

    def _assign_label(self, profile: dict) -> str:
        cpu = profile.get("cpu_usage", 0)
        mem = profile.get("memory_usage", 0)
        err = profile.get("error_rate", 0)
        lat = profile.get("latency_p99", 0)
        if err > 5 or (mem > 80 and cpu < 40):
            return "Degraded"
        elif cpu > 70:
            return "High Load"
        elif cpu < 30 and mem < 50:
            return "Baseline"
        elif lat > 500:
            return "High Latency"
        else:
            return "Normal"
