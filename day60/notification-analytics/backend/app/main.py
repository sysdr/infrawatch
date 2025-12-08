from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import random
import sys
import os

# Add backend directory to path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from models.schemas import init_db, MetricData, StatisticalBaseline, Anomaly, Prediction
from services.statistics.stats_service import stats_service
from services.anomaly.detector import anomaly_detector
from services.predictor.forecaster import forecaster
from services.correlation.analyzer import correlation_analyzer

app = FastAPI(title="Advanced Analytics API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
SessionLocal, engine = init_db()

# In-memory storage for demo
metrics_data = {}
anomalies_list = []

class MetricSubmit(BaseModel):
    metric_name: str
    metric_value: float
    tags: Optional[Dict] = {}

@app.on_event("startup")
async def startup_event():
    # Generate sample data with correlations
    metrics = ['notification_delivery_time', 'notification_failure_rate', 'notification_volume']
    
    # Initialize all metrics
    for metric in metrics:
        metrics_data[metric] = []
    
    # Generate correlated data
    base_volume = 1000
    for i in range(100):
        timestamp = datetime.utcnow() - timedelta(minutes=100-i)
        
        # Base volume with trend
        volume_base = base_volume + random.gauss(0, base_volume * 0.1)
        # Add some anomalies
        if i % 30 == 0:
            volume_base *= random.choice([1.5, 0.5])
        
        # Volume affects delivery time (positive correlation)
        # Higher volume -> longer delivery time
        delivery_time = 100 + (volume_base - base_volume) * 0.05 + random.gauss(0, 10)
        delivery_time = max(50, delivery_time)  # Ensure positive
        
        # Volume affects failure rate (positive correlation)
        # Higher volume -> higher failure rate
        failure_rate = 0.05 + (volume_base - base_volume) * 0.0001 + abs(random.gauss(0, 0.01))
        failure_rate = max(0.01, min(0.2, failure_rate))  # Keep in reasonable range
        
        metrics_data['notification_volume'].append({
            'value': volume_base,
            'timestamp': timestamp
        })
        metrics_data['notification_delivery_time'].append({
            'value': delivery_time,
            'timestamp': timestamp
        })
        metrics_data['notification_failure_rate'].append({
            'value': failure_rate,
            'timestamp': timestamp
        })

@app.post("/api/metrics")
async def submit_metric(metric: MetricSubmit, background_tasks: BackgroundTasks):
    if metric.metric_name not in metrics_data:
        metrics_data[metric.metric_name] = []
    
    metrics_data[metric.metric_name].append({
        'value': metric.metric_value,
        'timestamp': datetime.utcnow()
    })
    
    # Keep last 1000 points
    if len(metrics_data[metric.metric_name]) > 1000:
        metrics_data[metric.metric_name] = metrics_data[metric.metric_name][-1000:]
    
    background_tasks.add_task(analyze_metric, metric.metric_name, metric.metric_value)
    
    return {"status": "success"}

async def analyze_metric(metric_name: str, value: float):
    if metric_name not in metrics_data or len(metrics_data[metric_name]) < 10:
        return
    
    values = [d['value'] for d in metrics_data[metric_name][-100:]]
    stats = stats_service.calculate_stats(values)
    
    if stats:
        anomaly = anomaly_detector.detect_statistical_anomaly(
            value, stats['mean'], stats['std_dev']
        )
        
        if anomaly:
            anomalies_list.append({
                'id': len(anomalies_list) + 1,
                'metric_name': metric_name,
                'detected_at': datetime.utcnow().isoformat(),
                **anomaly
            })

@app.get("/api/statistics/{metric_name}")
async def get_statistics(metric_name: str, window_size: int = 3600):
    if metric_name not in metrics_data:
        raise HTTPException(status_code=404, detail="Metric not found")
    
    cutoff_time = datetime.utcnow() - timedelta(seconds=window_size)
    recent_data = [
        d['value'] for d in metrics_data[metric_name]
        if d['timestamp'] >= cutoff_time
    ]
    
    if not recent_data:
        raise HTTPException(status_code=404, detail="No recent data")
    
    stats = stats_service.calculate_stats(recent_data)
    
    return {
        "metric_name": metric_name,
        "window_size": window_size,
        "statistics": stats
    }

@app.get("/api/anomalies")
async def get_anomalies(
    metric_name: Optional[str] = None,
    hours: int = 24
):
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    filtered = anomalies_list
    if metric_name:
        filtered = [a for a in filtered if a['metric_name'] == metric_name]
    
    return {"anomalies": filtered[-100:], "count": len(filtered)}

@app.get("/api/predictions/{metric_name}")
async def get_predictions(metric_name: str, hours_ahead: int = 24):
    if metric_name not in metrics_data:
        raise HTTPException(status_code=404, detail="Metric not found")
    
    values = [d['value'] for d in metrics_data[metric_name][-100:]]
    predictions = []
    
    for hour in range(1, min(hours_ahead + 1, 25)):
        pred = forecaster.predict_next_value(values, hour)
        if pred:
            predictions.append({
                "hours_ahead": hour,
                "timestamp": (datetime.utcnow() + timedelta(hours=hour)).isoformat(),
                **pred
            })
    
    return {"metric_name": metric_name, "predictions": predictions}

@app.get("/api/correlations/{metric_name}")
async def get_correlations(metric_name: str):
    if metric_name not in metrics_data:
        raise HTTPException(status_code=404, detail="Metric not found")
    
    correlations = []
    target_values = [d['value'] for d in metrics_data[metric_name][-100:]]
    
    for other_metric, data in metrics_data.items():
        if other_metric == metric_name:
            continue
        
        other_values = [d['value'] for d in data[-100:]]
        corr = correlation_analyzer.calculate_correlation(target_values, other_values)
        
        if corr and abs(corr) >= 0.3:  # Lowered threshold to show moderate correlations
            strength = 'strong' if abs(corr) > 0.7 else ('moderate' if abs(corr) > 0.5 else 'weak')
            correlations.append({
                'metric': other_metric,
                'correlation': corr,
                'strength': strength
            })
    
    # Sort by absolute correlation value (strongest first)
    correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)
    
    return {"metric_name": metric_name, "correlated_metrics": correlations}

@app.get("/api/metrics")
async def list_metrics():
    return {"metrics": list(metrics_data.keys())}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
