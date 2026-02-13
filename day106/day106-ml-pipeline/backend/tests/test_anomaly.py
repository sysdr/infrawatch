import pytest
import pandas as pd
import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.ml.anomaly_detector import AnomalyDetector
from app.ml.pipeline import MLPipeline

def make_df(n=200):
    np.random.seed(0)
    return pd.DataFrame({
        "cpu_usage": np.clip(np.random.normal(40, 15, n), 0, 100),
        "memory_usage": np.clip(np.random.normal(55, 10, n), 0, 100),
        "request_rate": np.clip(np.random.normal(1000, 200, n), 0, None),
        "error_rate": np.clip(np.random.normal(1.0, 0.5, n), 0, 100),
        "latency_p99": np.clip(np.random.normal(150, 40, n), 0, None),
        "disk_io": np.clip(np.random.normal(30, 8, n), 0, 100),
        "network_in": np.clip(np.random.normal(500, 100, n), 0, None),
        "network_out": np.clip(np.random.normal(400, 80, n), 0, None)
    })

def test_anomaly_detector_trains():
    detector = AnomalyDetector(contamination=0.05)
    df = make_df(200)
    result = detector.train(df)
    assert detector.is_trained
    assert result["training_samples"] == 200

def test_anomaly_detector_scores():
    detector = AnomalyDetector(contamination=0.05)
    df = make_df(200)
    detector.train(df)
    score_result = detector.score(df.head(1))
    assert "is_anomaly" in score_result
    assert "anomaly_score" in score_result

def test_pipeline_generates_data():
    pipeline = MLPipeline()
    df = pipeline.generate_training_data(100)
    assert len(df) == 100
    assert "cpu_usage" in df.columns

def test_pipeline_trains_all():
    pipeline = MLPipeline()
    df = pipeline.generate_training_data(300)
    results = pipeline.train_all(df)
    assert "anomaly_detector" in results
    assert results["anomaly_detector"]["status"] == "trained"
    assert pipeline.is_pipeline_ready
