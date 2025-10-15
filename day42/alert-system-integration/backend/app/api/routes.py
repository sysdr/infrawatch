from fastapi import FastAPI, HTTPException
from typing import List
from datetime import datetime
from ..models import Alert, AlertRule, MetricData, AlertSeverity
from ..services.alert_evaluator import AlertEvaluator
from ..services.state_manager import StateManager
from ..services.notification_router import NotificationRouter

def create_routes(app: FastAPI, state_manager: StateManager, alert_evaluator: AlertEvaluator):
    
    @app.get("/api/alerts")
    async def get_alerts():
        """Get all alerts"""
        alerts = await state_manager.get_all_alerts()
        return {"alerts": [alert.dict() for alert in alerts]}
    
    @app.get("/api/alerts/firing")
    async def get_firing_alerts():
        """Get currently firing alerts"""
        alerts = await state_manager.get_firing_alerts()
        return {"alerts": [alert.dict() for alert in alerts]}
    
    @app.get("/api/alerts/{alert_id}")
    async def get_alert(alert_id: str):
        """Get specific alert"""
        alert = await state_manager.get_alert(alert_id)
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        return alert.dict()
    
    @app.get("/api/rules")
    async def get_rules():
        """Get all alert rules"""
        rules = await state_manager.get_all_rules()
        return {"rules": [rule.dict() for rule in rules]}
    
    @app.post("/api/rules")
    async def create_rule(rule: AlertRule):
        """Create new alert rule"""
        await state_manager.add_rule(rule)
        return {"message": "Rule created", "rule": rule.dict()}
    
    @app.post("/api/metrics")
    async def ingest_metrics(metrics: List[MetricData]):
        """Ingest metrics and trigger evaluation"""
        rules = await state_manager.get_all_rules()
        await alert_evaluator.evaluate_all_rules(rules, metrics)
        return {"message": f"Processed {len(metrics)} metrics"}
    
    @app.get("/api/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }
