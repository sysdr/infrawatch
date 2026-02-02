from pathlib import Path
from dotenv import load_dotenv
# Load .env from backend directory so DATABASE_URL etc. are set
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import asyncio
import json
from datetime import datetime

from app.models.database import init_db, get_db
from app.services.pattern_recognition import PatternRecognitionEngine
from app.services.anomaly_detection import AnomalyDetector
from app.services.trend_analysis import TrendAnalyzer
from app.services.alert_manager import AlertManager

app = FastAPI(title="Log Analysis System", version="1.0.0")

# CORS middleware: allow localhost and any host on 3001 (WSL IP when opened from Windows)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://127.0.0.1:3001"],
    allow_origin_regex=r"http://[\w.-]+:3001",  # e.g. http://172.22.24.182:3001
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    init_db()
    print("Database initialized")

@app.get("/")
async def root():
    return {"message": "Log Analysis System API", "version": "1.0.0"}

@app.post("/api/logs/analyze")
async def analyze_log(
    log_data: dict,
    db: Session = Depends(get_db)
):
    """
    Analyze incoming log and detect patterns/anomalies.
    Simulates the real-time analysis pipeline.
    """
    message = log_data.get("message", "")
    level = log_data.get("level", "INFO")
    source = log_data.get("source", "unknown")
    metrics = log_data.get("metrics", {})
    
    results = {
        "timestamp": datetime.utcnow().isoformat(),
        "pattern": None,
        "anomalies": [],
        "alerts": []
    }
    
    # Pattern recognition
    pattern_engine = PatternRecognitionEngine(db)
    pattern = pattern_engine.match_or_create_pattern(message, level, source)
    
    if pattern:
        results["pattern"] = {
            "id": pattern.id,
            "template": pattern.pattern_template,
            "category": pattern.category,
            "severity": pattern.severity,
            "frequency": pattern.frequency_count
        }
        
        # Check for frequency spike (simple threshold for demo)
        if pattern.frequency_count > 100 and pattern.frequency_count % 50 == 0:
            alert_mgr = AlertManager(db)
            alert = alert_mgr.create_pattern_alert(pattern, frequency_spike=True)
            if alert:
                results["alerts"].append({
                    "id": alert.id,
                    "title": alert.title,
                    "severity": alert.severity
                })
    
    # Anomaly detection on metrics
    if metrics:
        anomaly_detector = AnomalyDetector(db)
        
        for metric_name, metric_value in metrics.items():
            anomaly = anomaly_detector.detect_zscore_anomaly(
                metric_name, metric_value, source
            )
            
            if anomaly:
                results["anomalies"].append({
                    "id": anomaly.id,
                    "metric": metric_name,
                    "value": metric_value,
                    "z_score": anomaly.z_score,
                    "type": anomaly.anomaly_type
                })
                
                # Create alert for critical anomalies
                if anomaly.severity == 'critical':
                    alert_mgr = AlertManager(db)
                    alert = alert_mgr.create_anomaly_alert(anomaly)
                    if alert:
                        results["alerts"].append({
                            "id": alert.id,
                            "title": alert.title,
                            "severity": alert.severity
                        })
        
        # Record metrics for trend analysis
        trend_analyzer = TrendAnalyzer(db)
        for metric_name, metric_value in metrics.items():
            trend_analyzer.record_metric(metric_name, metric_value)
    
    # Broadcast to WebSocket clients
    await manager.broadcast({
        "type": "analysis_result",
        "data": results
    })
    
    return results

@app.get("/api/patterns")
async def get_patterns(
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """Get pattern statistics"""
    pattern_engine = PatternRecognitionEngine(db)
    return pattern_engine.get_pattern_statistics(hours=hours)

@app.get("/api/anomalies")
async def get_anomalies(
    hours: int = 24,
    resolved: bool = False,
    db: Session = Depends(get_db)
):
    """Get recent anomalies"""
    anomaly_detector = AnomalyDetector(db)
    return anomaly_detector.get_recent_anomalies(hours=hours, resolved=resolved)

@app.get("/api/trends")
async def get_trends(
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """Get trend analysis summary"""
    trend_analyzer = TrendAnalyzer(db)
    return trend_analyzer.get_trend_summary(hours=hours)

@app.get("/api/alerts")
async def get_alerts(
    severity: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get active alerts"""
    alert_mgr = AlertManager(db)
    return alert_mgr.get_active_alerts(severity=severity)

@app.get("/api/alerts/statistics")
async def get_alert_statistics(
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """Get alert statistics"""
    alert_mgr = AlertManager(db)
    return alert_mgr.get_alert_statistics(hours=hours)

@app.post("/api/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    db: Session = Depends(get_db)
):
    """Acknowledge an alert"""
    alert_mgr = AlertManager(db)
    success = alert_mgr.acknowledge_alert(alert_id)
    if success:
        await manager.broadcast({
            "type": "alert_acknowledged",
            "alert_id": alert_id
        })
        return {"status": "acknowledged"}
    raise HTTPException(status_code=404, detail="Alert not found")

@app.post("/api/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_db)
):
    """Resolve an alert"""
    alert_mgr = AlertManager(db)
    success = alert_mgr.resolve_alert(alert_id)
    if success:
        await manager.broadcast({
            "type": "alert_resolved",
            "alert_id": alert_id
        })
        return {"status": "resolved"}
    raise HTTPException(status_code=404, detail="Alert not found")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for testing
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

# Demo seed data - diverse logs to populate patterns, anomalies, trends, alerts
DEMO_LOGS = [
    {"message": "User 10042 logged in successfully from IP 192.168.1.100", "level": "INFO", "metrics": {"response_time": 45, "error_rate": 0.1}},
    {"message": "API request processed in 23ms", "level": "INFO", "metrics": {"response_time": 23, "error_rate": 0.1}},
    {"message": "Database query executed successfully", "level": "INFO", "metrics": {"response_time": 34, "error_rate": 0.1}},
    {"message": "User 20088 logged in successfully from IP 10.0.0.15", "level": "INFO", "metrics": {"response_time": 52, "error_rate": 0.2}},
    {"message": "API request processed in 19ms", "level": "INFO", "metrics": {"response_time": 19, "error_rate": 0.1}},
    {"message": "Failed to connect to database timeout after 30s", "level": "ERROR", "metrics": {"response_time": 30000, "error_rate": 15}},
    {"message": "Authentication failed for user 98765", "level": "ERROR", "metrics": {"response_time": 67, "error_rate": 12}},
    {"message": "User 30421 logged in from IP 172.16.0.22", "level": "INFO", "metrics": {"response_time": 38, "error_rate": 0.1}},
    {"message": "Request processed", "level": "INFO", "metrics": {"response_time": 5000, "error_rate": 25}},
    {"message": "Critical service unavailable", "level": "CRITICAL", "metrics": {"response_time": 5000, "error_rate": 20}},
    {"message": "Unusual traffic pattern detected", "level": "WARN", "metrics": {"response_time": 3456, "error_rate": 18}},
    {"message": "API request processed in 28ms", "level": "INFO", "metrics": {"response_time": 28, "error_rate": 0.1}},
    {"message": "Database connection pool exhausted", "level": "ERROR", "metrics": {"response_time": 15000, "error_rate": 8}},
    {"message": "User 45001 logged in from IP 192.168.2.50", "level": "INFO", "metrics": {"response_time": 41, "error_rate": 0.1}},
    {"message": "Cache hit for key session:user:45001", "level": "INFO", "metrics": {"response_time": 2, "error_rate": 0}},
    {"message": "Request processed", "level": "INFO", "metrics": {"response_time": 42, "error_rate": 0.2}},
    {"message": "API request processed in 31ms", "level": "INFO", "metrics": {"response_time": 31, "error_rate": 0.1}},
    {"message": "Disk space critical on /var/log", "level": "WARN", "metrics": {"response_time": 100, "error_rate": 5}},
    {"message": "User 55002 logged in from IP 10.10.10.100", "level": "INFO", "metrics": {"response_time": 48, "error_rate": 0.1}},
    {"message": "Request processed", "level": "INFO", "metrics": {"response_time": 89, "error_rate": 1.5}},
    {"message": "Connection refused to upstream service", "level": "ERROR", "metrics": {"response_time": 5000, "error_rate": 22}},
    {"message": "User 66003 logged in from IP 172.20.1.33", "level": "INFO", "metrics": {"response_time": 36, "error_rate": 0.1}},
    {"message": "API request processed in 25ms", "level": "INFO", "metrics": {"response_time": 25, "error_rate": 0.1}},
    {"message": "Request processed", "level": "INFO", "metrics": {"response_time": 5200, "error_rate": 28}},
    {"message": "SSL certificate expired for api.example.com", "level": "WARN", "metrics": {"response_time": 200, "error_rate": 10}},
    {"message": "User 77004 logged in from IP 192.168.5.12", "level": "INFO", "metrics": {"response_time": 44, "error_rate": 0.2}},
    {"message": "Database query executed successfully", "level": "INFO", "metrics": {"response_time": 29, "error_rate": 0.1}},
    {"message": "Memory usage above 90% threshold", "level": "WARN", "metrics": {"response_time": 150, "error_rate": 3}},
    {"message": "User 88005 logged in from IP 10.0.1.200", "level": "INFO", "metrics": {"response_time": 39, "error_rate": 0.1}},
    {"message": "API request processed in 21ms", "level": "INFO", "metrics": {"response_time": 21, "error_rate": 0.1}},
    {"message": "Request processed", "level": "INFO", "metrics": {"response_time": 51, "error_rate": 0.3}},
    {"message": "Rate limit exceeded for client 203.0.113.45", "level": "WARN", "metrics": {"response_time": 429, "error_rate": 15}},
]

@app.post("/api/demo/seed")
async def seed_demo_data(db: Session = Depends(get_db)):
    """Seed the database with demo logs to showcase dashboard functionality."""
    count = 0
    for log_data in DEMO_LOGS:
        message = log_data.get("message", "")
        level = log_data.get("level", "INFO")
        source = "demo_seed"
        metrics = log_data.get("metrics", {})
        pattern_engine = PatternRecognitionEngine(db)
        pattern = pattern_engine.match_or_create_pattern(message, level, source)
        if pattern and pattern.frequency_count > 100 and pattern.frequency_count % 50 == 0:
            alert_mgr = AlertManager(db)
            alert_mgr.create_pattern_alert(pattern, frequency_spike=True)
        if metrics:
            anomaly_detector = AnomalyDetector(db)
            for metric_name, metric_value in metrics.items():
                anomaly = anomaly_detector.detect_zscore_anomaly(metric_name, metric_value, source)
                if anomaly and anomaly.severity == 'critical':
                    alert_mgr = AlertManager(db)
                    alert_mgr.create_anomaly_alert(anomaly)
            trend_analyzer = TrendAnalyzer(db)
            for metric_name, metric_value in metrics.items():
                trend_analyzer.record_metric(metric_name, metric_value)
        count += 1
    await manager.broadcast({"type": "demo_seeded", "count": count})
    return {"status": "ok", "logs_processed": count, "message": "Demo data loaded. Check Patterns, Anomalies, Trends, and Alerts tabs."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
