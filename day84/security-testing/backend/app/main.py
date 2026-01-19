from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.core.database import get_db, engine, Base
from app.testing.framework import SecurityTestFramework, IntegrationTestFramework
from app.chaos.attack_simulator import ChaosTestEngine
from app.assessment.security_audit import SecurityAssessmentEngine
from app.models.security import SecurityEvent, SecurityTest, IncidentResponse
from typing import Dict, Any, List
from datetime import datetime, timedelta
import asyncio

app = FastAPI(title="Security Testing Platform", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Security Testing Platform API", "version": "1.0.0"}

@app.post("/api/tests/unit/run")
async def run_unit_tests(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Execute all unit tests"""
    framework = SecurityTestFramework(db)
    results = await framework.run_unit_tests()
    return results

@app.post("/api/tests/integration/run")
async def run_integration_tests(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Execute integration tests"""
    framework = IntegrationTestFramework(db)
    results = await framework.run_integration_tests()
    return results

@app.post("/api/tests/chaos/run")
async def run_chaos_tests(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Execute chaos attack simulations"""
    engine = ChaosTestEngine(db)
    results = await engine.run_chaos_tests()
    return results

@app.post("/api/assessment/run")
async def run_security_assessment(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Run comprehensive security assessment"""
    assessor = SecurityAssessmentEngine(db)
    results = await assessor.run_comprehensive_assessment()
    return results

@app.get("/api/events")
async def get_security_events(
    limit: int = 100,
    event_type: str = None,
    severity: str = None,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get security events"""
    query = db.query(SecurityEvent)
    
    if event_type:
        query = query.filter(SecurityEvent.event_type == event_type)
    if severity:
        query = query.filter(SecurityEvent.severity == severity)
    
    events = query.order_by(SecurityEvent.detected_at.desc()).limit(limit).all()
    
    return [{
        "id": e.id,
        "event_type": e.event_type,
        "severity": e.severity,
        "source_ip": e.source_ip,
        "endpoint": e.endpoint,
        "threat_score": e.threat_score,
        "detected_at": e.detected_at.isoformat() if e.detected_at else None,
        "response_status": e.response_status
    } for e in events]

@app.get("/api/tests/results")
async def get_test_results(
    test_type: str = None,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get test results"""
    query = db.query(SecurityTest)
    
    if test_type:
        query = query.filter(SecurityTest.test_type == test_type)
    
    tests = query.order_by(SecurityTest.started_at.desc()).limit(50).all()
    
    return [{
        "id": t.id,
        "test_name": t.test_name,
        "test_type": t.test_type,
        "status": t.status,
        "duration_ms": t.duration_ms,
        "started_at": t.started_at.isoformat() if t.started_at else None,
        "results": t.results
    } for t in tests]

@app.get("/api/incidents")
async def get_incidents(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Get security incidents"""
    incidents = db.query(IncidentResponse).order_by(
        IncidentResponse.first_detected.desc()
    ).limit(50).all()
    
    return [{
        "id": i.id,
        "incident_id": i.incident_id,
        "severity": i.severity,
        "status": i.status,
        "event_count": i.event_count,
        "first_detected": i.first_detected.isoformat() if i.first_detected else None,
        "affected_systems": i.affected_systems,
        "response_actions": i.response_actions
    } for i in incidents]

@app.get("/api/dashboard/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get dashboard statistics"""
    # Get events from last 24 hours
    since = datetime.utcnow() - timedelta(hours=24)
    
    total_events = db.query(SecurityEvent).filter(
        SecurityEvent.detected_at >= since
    ).count()
    
    critical_events = db.query(SecurityEvent).filter(
        SecurityEvent.detected_at >= since,
        SecurityEvent.severity == "critical"
    ).count()
    
    active_incidents = db.query(IncidentResponse).filter(
        IncidentResponse.status.in_(["detected", "investigating"])
    ).count()
    
    recent_tests = db.query(SecurityTest).filter(
        SecurityTest.started_at >= since
    ).count()
    
    passed_tests = db.query(SecurityTest).filter(
        SecurityTest.started_at >= since,
        SecurityTest.status == "passed"
    ).count()
    
    test_pass_rate = (passed_tests / recent_tests * 100) if recent_tests > 0 else 0
    
    return {
        "total_events_24h": total_events,
        "critical_events_24h": critical_events,
        "active_incidents": active_incidents,
        "tests_run_24h": recent_tests,
        "test_pass_rate": round(test_pass_rate, 2),
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
