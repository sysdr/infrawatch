from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
import logging

from ..ml.pipeline import MLPipeline

router = APIRouter(prefix="/api/v1/ml", tags=["ml-pipeline"])
logger = logging.getLogger(__name__)

def get_pipeline() -> MLPipeline:
    return MLPipeline.get_instance()

@router.post("/train")
async def train_pipeline(n_samples: int = Query(default=500, ge=100, le=2000)):
    pipeline = get_pipeline()
    try:
        df = pipeline.generate_training_data(n_samples)
        results = pipeline.train_all(df)
        return {
            "status": "trained",
            "training_samples": n_samples,
            "trained_at": datetime.utcnow().isoformat(),
            "results": results
        }
    except Exception as e:
        logger.error(f"Training failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def pipeline_status():
    pipeline = get_pipeline()
    return {
        "is_ready": pipeline.is_pipeline_ready,
        "last_trained": pipeline.last_trained.isoformat() if pipeline.last_trained else None,
        "anomaly_detector_ready": pipeline.anomaly_detector.is_trained,
        "forecast_ready": pipeline.predictive_analytics.is_trained,
        "pattern_ready": pipeline.pattern_recognizer.is_trained
    }

@router.get("/anomalies/latest")
async def get_latest_anomaly():
    pipeline = get_pipeline()
    if not pipeline.is_pipeline_ready:
        raise HTTPException(status_code=400, detail="Pipeline not trained. POST /api/v1/ml/train first.")
    result = pipeline.infer_current()
    return result

@router.get("/anomalies/batch")
async def get_batch_anomalies(n_points: int = Query(default=50, ge=10, le=200)):
    pipeline = get_pipeline()
    if not pipeline.is_pipeline_ready:
        raise HTTPException(status_code=400, detail="Pipeline not trained.")
    df = pipeline.generate_training_data(n_points)
    batch = pipeline.anomaly_detector.batch_score(df)
    pca_all = pipeline.pattern_recognizer.predict(df)

    results = []
    for i, (b, p) in enumerate(zip(batch, pca_all)):
        results.append({
            "index": i,
            "cpu_usage": float(df.iloc[i]["cpu_usage"]),
            "memory_usage": float(df.iloc[i]["memory_usage"]),
            "error_rate": float(df.iloc[i]["error_rate"]),
            "latency_p99": float(df.iloc[i]["latency_p99"]),
            **b,
            "cluster_id": p["cluster_id"],
            "cluster_label": p["cluster_label"]
        })
    return {"data": results, "total": len(results)}

@router.get("/forecast")
async def get_forecast(metric: str = Query(default="cpu_usage")):
    pipeline = get_pipeline()
    if not pipeline.is_pipeline_ready:
        raise HTTPException(status_code=400, detail="Pipeline not trained.")
    if not pipeline.predictive_analytics.is_trained:
        raise HTTPException(status_code=400, detail="Forecast model not trained.")
    try:
        result = pipeline.predictive_analytics.forecast(metric)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/forecast/all")
async def get_all_forecasts():
    pipeline = get_pipeline()
    if not pipeline.is_pipeline_ready:
        raise HTTPException(status_code=400, detail="Pipeline not trained.")
    return pipeline.predictive_analytics.forecast_all()

@router.get("/patterns")
async def get_patterns():
    pipeline = get_pipeline()
    if not pipeline.is_pipeline_ready:
        raise HTTPException(status_code=400, detail="Pipeline not trained.")
    n_samples = 100
    df = pipeline.generate_training_data(n_samples)
    predictions = pipeline.pattern_recognizer.predict(df)
    profiles = pipeline.pattern_recognizer.cluster_profiles
    return {
        "points": predictions,
        "cluster_profiles": profiles,
        "silhouette_score": pipeline.pattern_recognizer.silhouette,
        "n_clusters": pipeline.pattern_recognizer.n_clusters
    }

@router.get("/evaluation")
async def get_evaluation():
    pipeline = get_pipeline()
    if not pipeline.is_pipeline_ready:
        raise HTTPException(status_code=400, detail="Pipeline not trained.")
    return pipeline.get_evaluation()

@router.post("/reset")
async def reset_pipeline():
    MLPipeline._instance = None
    return {"status": "reset", "message": "Pipeline instance cleared. Re-train with POST /api/v1/ml/train"}
