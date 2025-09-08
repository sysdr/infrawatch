from celery import chain, group, chord
from config.celery_config import celery_app
from . import metric_tasks, notification_tasks, report_tasks, maintenance_tasks

@celery_app.task
def create_metric_analysis_chain(metric_name):
    """Chain tasks for comprehensive metric analysis"""
    
    # Create a chain: collect -> analyze -> report -> notify if needed
    analysis_chain = chain(
        metric_tasks.collect_custom_metric.s(metric_name, 0, "percent", "analysis"),
        report_tasks.generate_trend_analysis.s(metric_name, 24),
        decide_notification_action.s()
    )
    
    return analysis_chain.apply_async()

@celery_app.task
def decide_notification_action(trend_analysis):
    """Decide whether to send notifications based on trend analysis"""
    
    if trend_analysis.get("trend_direction") == "increasing" and trend_analysis.get("current_value", 0) > 80:
        # Chain notification tasks
        notification_chain = chain(
            notification_tasks.send_threshold_alert.s(
                metric_name=trend_analysis["metric_name"],
                value=trend_analysis["current_value"], 
                threshold=80
            ),
            report_tasks.generate_dashboard_summary.s()
        )
        return notification_chain.apply_async()
    
    return {"action": "no_notification_needed", "analysis": trend_analysis}

@celery_app.task
def create_maintenance_workflow():
    """Create comprehensive maintenance workflow"""
    
    # Use chord to run maintenance tasks in parallel, then generate summary
    maintenance_group = group(
        maintenance_tasks.cleanup_old_data.s(),
        maintenance_tasks.optimize_database.s(),
        maintenance_tasks.health_check_system.s(),
        maintenance_tasks.archive_old_reports.s()
    )
    
    maintenance_workflow = chord(maintenance_group)(summarize_maintenance.s())
    
    return maintenance_workflow

@celery_app.task
def summarize_maintenance(results):
    """Summarize maintenance workflow results"""
    
    summary = {
        "maintenance_completed": True,
        "results": results,
        "total_tasks": len(results),
        "successful_tasks": len([r for r in results if isinstance(r, dict) and not r.get("error")]),
        "completed_at": time.time()
    }
    
    # Store summary in Redis
    import redis
    import json
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    redis_client.setex("maintenance:last_summary", 86400, json.dumps(summary))
    
    return summary

@celery_app.task  
def create_alert_escalation_chain(metric_name, value, initial_threshold):
    """Create escalation chain for persistent alerts"""
    
    escalation_chain = chain(
        # First alert
        notification_tasks.send_slack_notification.s(
            message=f"🟡 Warning: {metric_name} at {value}% (threshold: {initial_threshold}%)",
            channel="#alerts"
        ),
        # Wait and check again (implemented via delay)
        check_metric_persistence.s(metric_name, initial_threshold),
        # Escalate if still high
        escalate_alert_if_needed.s(metric_name, value)
    )
    
    return escalation_chain.apply_async()

@celery_app.task
def check_metric_persistence(previous_result, metric_name, threshold):
    """Check if metric issue persists"""
    import time
    time.sleep(300)  # Wait 5 minutes
    
    # Get current metric value
    from models.base import SessionLocal
    from models.metric import Metric
    from datetime import datetime, timedelta
    
    with SessionLocal() as db:
        recent_time = datetime.utcnow() - timedelta(minutes=2)
        recent_metric = db.query(Metric).filter(
            Metric.name == metric_name,
            Metric.created_at >= recent_time
        ).order_by(Metric.created_at.desc()).first()
    
    current_value = recent_metric.value if recent_metric else 0
    
    return {
        "metric_name": metric_name,
        "current_value": current_value,
        "threshold": threshold,
        "persists": current_value > threshold,
        "previous_result": previous_result
    }

@celery_app.task
def escalate_alert_if_needed(persistence_result, metric_name, original_value):
    """Escalate alert if issue persists"""
    
    if persistence_result.get("persists"):
        # Escalate to email and webhook
        escalation_chain = group(
            notification_tasks.send_email_notification.s(
                subject=f"🔴 ESCALATED ALERT: {metric_name}",
                message=f"Critical: {metric_name} has been above threshold for 5+ minutes. Current: {persistence_result['current_value']}%",
                recipient="admin@example.com"
            ),
            notification_tasks.send_webhook_notification.s(
                url="http://localhost:8000/webhook/escalation",
                payload={
                    "alert_level": "critical",
                    "metric": metric_name,
                    "value": persistence_result['current_value'],
                    "duration_minutes": 5
                }
            )
        )
        
        return escalation_chain.apply_async()
    
    return {"escalation": "not_needed", "metric": metric_name}

import time
