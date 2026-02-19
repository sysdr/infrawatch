import pytest
import time
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
from app.services.data_generator import seed_database

TEST_DB = "sqlite:///./test_ml.db"
engine  = create_engine(TEST_DB, connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def override_db():
    db = TestSession()
    try:
        seed_database(db, days=30)
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_db
client = TestClient(app)

def test_ml_status_idle():
    r = client.get("/api/ml/status")
    assert r.status_code == 200
    data = r.json()
    assert "status" in data

def test_ml_train_trigger():
    r = client.post("/api/ml/train")
    assert r.status_code == 200
    assert "training_started" in r.json()["status"]

def test_ml_train_and_predict():
    # Synchronous training for test
    from app.ml.trainer import train_models, _ml_state
    from sqlalchemy.orm import Session
    from app.models.analytics import HourlyMetric

    db = TestSession()
    try:
        seed_database(db, days=30)
        rows = db.query(HourlyMetric).all()
        assert len(rows) >= 48, f"Expected >= 48 rows, got {len(rows)}"
        result = train_models(rows)
        assert result["status"] == "serving"
        assert "r2" in result["metrics"]
        assert result["metrics"]["r2"] > -0.5  # can be slightly negative on small/noisy data
    finally:
        db.close()

def test_predictions():
    from app.ml.predictor import predict_next_hours
    preds = predict_next_hours(12)
    assert len(preds) == 12
    for p in preds:
        assert "predicted" in p
        assert "upper" in p
        assert "lower" in p
        assert p["upper"] >= p["predicted"] >= p["lower"]

def test_anomaly_detection():
    from app.ml.predictor import detect_anomalies
    db = TestSession()
    try:
        from app.models.analytics import HourlyMetric
        rows = db.query(HourlyMetric).all()
        results = detect_anomalies(rows)
        assert isinstance(results, list)
        assert len(results) > 0
        flagged = [r for r in results if r["is_anomaly"]]
        assert len(flagged) >= 1, "Expected at least 1 anomaly in seeded data"
    finally:
        db.close()

def test_correlations():
    r = client.get("/api/ml/correlations?method=pearson")
    assert r.status_code == 200
    data = r.json()
    assert "matrix" in data
    assert "metrics" in data
    assert len(data["matrix"]) == 5
    assert len(data["matrix"][0]) == 5
    # Diagonal should be 1.0
    for i in range(5):
        assert abs(data["matrix"][i][i] - 1.0) < 0.001
