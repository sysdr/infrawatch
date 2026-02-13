import numpy as np
import pandas as pd
from datetime import datetime
import random
import logging
from .anomaly_detector import AnomalyDetector
from .predictive_analytics import PredictiveAnalytics
from .pattern_recognition import PatternRecognizer
from .model_evaluator import ModelEvaluator
from ..config import settings

logger = logging.getLogger(__name__)

class MLPipeline:
    _instance = None

    def __init__(self):
        self.anomaly_detector = AnomalyDetector(contamination=settings.contamination)
        self.predictive_analytics = PredictiveAnalytics(forecast_steps=settings.forecast_steps)
        self.pattern_recognizer = PatternRecognizer(n_clusters=settings.n_clusters)
        self.evaluator = ModelEvaluator(
            self.anomaly_detector,
            self.predictive_analytics,
            self.pattern_recognizer
        )
        self.is_pipeline_ready = False
        self.training_data: pd.DataFrame = pd.DataFrame()
        self.last_trained: datetime = None
        self.train_results: dict = {}

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def generate_training_data(self, n_samples: int = 500) -> pd.DataFrame:
        np.random.seed(42)
        random.seed(42)

        t = np.linspace(0, 4 * np.pi, n_samples)
        base_cpu = 35 + 20 * np.sin(t) + np.random.normal(0, 5, n_samples)
        base_memory = 50 + 10 * np.sin(t / 2) + np.random.normal(0, 3, n_samples)
        base_requests = 1000 + 500 * np.sin(t) + np.random.normal(0, 50, n_samples)
        base_errors = 0.5 + 0.3 * np.abs(np.sin(t * 2)) + np.random.normal(0, 0.1, n_samples)
        base_latency = 120 + 50 * np.sin(t) + np.random.normal(0, 10, n_samples)
        base_disk = 30 + 5 * np.sin(t / 3) + np.random.normal(0, 2, n_samples)
        base_net_in = 500 + 200 * np.sin(t) + np.random.normal(0, 20, n_samples)
        base_net_out = 400 + 150 * np.sin(t) + np.random.normal(0, 15, n_samples)

        anomaly_indices = np.random.choice(n_samples, size=int(n_samples * 0.05), replace=False)
        for idx in anomaly_indices:
            atype = random.choice(["cpu_spike", "memory_leak", "error_surge", "latency_spike"])
            if atype == "cpu_spike":
                base_cpu[idx] = np.random.uniform(90, 100)
                base_requests[idx] = np.random.uniform(2500, 3500)
            elif atype == "memory_leak":
                base_memory[idx] = np.random.uniform(88, 98)
                base_latency[idx] = np.random.uniform(450, 800)
            elif atype == "error_surge":
                base_errors[idx] = np.random.uniform(15, 35)
                base_latency[idx] = np.random.uniform(600, 1200)
            elif atype == "latency_spike":
                base_latency[idx] = np.random.uniform(1000, 3000)
                base_errors[idx] = np.random.uniform(5, 20)

        df = pd.DataFrame({
            "cpu_usage": np.clip(base_cpu, 0, 100),
            "memory_usage": np.clip(base_memory, 0, 100),
            "request_rate": np.clip(base_requests, 0, None),
            "error_rate": np.clip(base_errors, 0, 100),
            "latency_p99": np.clip(base_latency, 0, None),
            "disk_io": np.clip(base_disk, 0, 100),
            "network_in": np.clip(base_net_in, 0, None),
            "network_out": np.clip(base_net_out, 0, None)
        })
        return df

    def train_all(self, df: pd.DataFrame = None) -> dict:
        if df is None:
            df = self.generate_training_data(500)
        self.training_data = df

        results = {}
        try:
            ad_result = self.anomaly_detector.train(df)
            results["anomaly_detector"] = {"status": "trained", **ad_result}
        except Exception as e:
            results["anomaly_detector"] = {"status": "failed", "error": str(e)}

        try:
            fc_result = self.predictive_analytics.train(df)
            results["predictive_analytics"] = {"status": "trained", "metrics": fc_result}
        except Exception as e:
            results["predictive_analytics"] = {"status": "failed", "error": str(e)}

        try:
            pr_result = self.pattern_recognizer.fit(df)
            results["pattern_recognizer"] = {"status": "trained", **pr_result}
        except Exception as e:
            results["pattern_recognizer"] = {"status": "failed", "error": str(e)}

        self.is_pipeline_ready = True
        self.last_trained = datetime.utcnow()
        self.train_results = results
        return results

    def infer_current(self) -> dict:
        if not self.is_pipeline_ready:
            raise RuntimeError("Pipeline not trained. Call /api/v1/ml/train first.")

        np.random.seed(int(datetime.utcnow().timestamp()) % 10000)
        inject_anomaly = random.random() < 0.12

        if inject_anomaly:
            atype = random.choice(["cpu_spike", "memory_leak", "error_surge"])
            if atype == "cpu_spike":
                row = {"cpu_usage": random.uniform(88, 99), "memory_usage": random.uniform(50, 70),
                       "request_rate": random.uniform(2200, 3200), "error_rate": random.uniform(0.5, 2),
                       "latency_p99": random.uniform(300, 600), "disk_io": random.uniform(30, 60),
                       "network_in": random.uniform(600, 1200), "network_out": random.uniform(500, 1000)}
            elif atype == "memory_leak":
                row = {"cpu_usage": random.uniform(30, 50), "memory_usage": random.uniform(90, 98),
                       "request_rate": random.uniform(800, 1200), "error_rate": random.uniform(1, 5),
                       "latency_p99": random.uniform(400, 900), "disk_io": random.uniform(20, 40),
                       "network_in": random.uniform(400, 700), "network_out": random.uniform(350, 600)}
            else:
                row = {"cpu_usage": random.uniform(40, 65), "memory_usage": random.uniform(55, 75),
                       "request_rate": random.uniform(1000, 1500), "error_rate": random.uniform(18, 35),
                       "latency_p99": random.uniform(700, 1500), "disk_io": random.uniform(25, 45),
                       "network_in": random.uniform(450, 750), "network_out": random.uniform(400, 650)}
        else:
            row = {"cpu_usage": random.uniform(25, 65), "memory_usage": random.uniform(35, 75),
                   "request_rate": random.uniform(500, 1800), "error_rate": random.uniform(0.1, 1.5),
                   "latency_p99": random.uniform(80, 280), "disk_io": random.uniform(15, 50),
                   "network_in": random.uniform(200, 700), "network_out": random.uniform(180, 600)}

        df = pd.DataFrame([row])
        anomaly_result = self.anomaly_detector.score(df)
        pattern_result = self.pattern_recognizer.predict(df)

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": row,
            "anomaly": anomaly_result,
            "pattern": pattern_result[0] if pattern_result else {},
        }

    def get_evaluation(self) -> dict:
        if not self.is_pipeline_ready:
            return {"error": "Pipeline not trained"}
        return self.evaluator.evaluate(self.training_data)
