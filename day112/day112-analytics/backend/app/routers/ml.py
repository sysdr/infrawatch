from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.analytics import HourlyMetric
from app.ml.trainer import train_models, get_ml_status
from app.ml.predictor import predict_next_hours, detect_anomalies
from app.services.correlation import compute_correlation_matrix

router = APIRouter()

def _do_train(db: Session):
    rows = db.query(HourlyMetric).order_by(HourlyMetric.hour_bucket).all()
    train_models(rows)

@router.post("/train")
def trigger_training(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    background_tasks.add_task(_do_train, db)
    return {"status": "training_started", "message": "Training running in background. Poll /api/ml/status"}

@router.get("/status")
def ml_status():
    return get_ml_status()

@router.get("/predict")
def predictions(hours: int = 24):
    try:
        data = predict_next_hours(hours)
        return {"hours": hours, "predictions": data, "count": len(data)}
    except RuntimeError as e:
        return {"error": str(e), "predictions": []}

@router.get("/anomalies")
def anomalies(db: Session = Depends(get_db)):
    rows = db.query(HourlyMetric).order_by(HourlyMetric.hour_bucket).all()
    try:
        data = detect_anomalies(rows)
        flagged = [d for d in data if d["is_anomaly"]]
        return {"total_points": len(data), "anomalies_found": len(flagged), "data": data}
    except RuntimeError as e:
        return {"error": str(e), "data": []}

@router.get("/correlations")
def correlations(method: str = "pearson", db: Session = Depends(get_db)):
    rows = db.query(HourlyMetric).order_by(HourlyMetric.hour_bucket).all()
    return compute_correlation_matrix(rows, method)
