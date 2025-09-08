from celery import Task, chain
from config.celery_config import celery_app
from models.notification import Notification
from models.base import SessionLocal
import time
import json
import hashlib
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=3)

@celery_app.task(bind=True)
def send_threshold_alert(self, metric_name, value, threshold, channels=None):
    """Send alert when metric exceeds threshold"""
    try:
        channels = channels or ["email", "slack"]
        
        # Create group key for alert grouping
        group_key = hashlib.md5(f"{metric_name}:{threshold}".encode()).hexdigest()
        
        # Check if we've sent this alert recently (exponential backoff)
        cooldown_key = f"alert_cooldown:{group_key}"
        if redis_client.exists(cooldown_key):
            return {"status": "suppressed", "reason": "cooldown_active"}
        
        message = f"🚨 ALERT: {metric_name} is at {value}% (threshold: {threshold}%)"
        
        # Try each channel with fallback
        results = []
        for channel in channels:
            try:
                if channel == "email":
                    result = send_email_notification.delay(
                        subject="Metric Alert",
                        message=message,
                        recipient="admin@example.com"
                    ).get()
                elif channel == "slack":
                    result = send_slack_notification.delay(
                        message=message,
                        channel="#alerts"
                    ).get()
                elif channel == "webhook":
                    result = send_webhook_notification.delay(
                        url="http://localhost:8000/webhook/alert",
                        payload={"metric": metric_name, "value": value, "threshold": threshold}
                    ).get()
                
                results.append({"channel": channel, "status": "sent", "result": result})
                break  # Success - don't try other channels
                
            except Exception as channel_error:
                results.append({"channel": channel, "status": "failed", "error": str(channel_error)})
                continue
        
        # Set cooldown (exponential backoff: 1min, 5min, 15min)
        cooldown_seconds = min(900, 60 * (3 ** len(results)))  # Max 15 minutes
        redis_client.setex(cooldown_key, cooldown_seconds, "1")
        
        # Store notification record
        with SessionLocal() as db:
            notification = Notification(
                title="Threshold Alert",
                message=message,
                channel=",".join(channels),
                recipient="system",
                status="sent" if any(r["status"] == "sent" for r in results) else "failed",
                meta_data={"results": results, "group_key": group_key},
                is_grouped=True,
                group_key=group_key
            )
            db.add(notification)
            db.commit()
        
        return {"alert_sent": True, "channels_tried": len(channels), "results": results}
        
    except Exception as e:
        self.retry(exc=e, countdown=120, max_retries=2)

@celery_app.task(bind=True)
def send_email_notification(self, subject, message, recipient):
    """Send email notification (mock implementation)"""
    try:
        # In production, integrate with SendGrid, SES, or similar
        time.sleep(0.5)  # Simulate email sending delay
        
        notification_id = f"email_{int(time.time())}"
        
        # Log notification
        with SessionLocal() as db:
            notification = Notification(
                title=subject,
                message=message,
                channel="email",
                recipient=recipient,
                status="sent",
                meta_data={"notification_id": notification_id}
            )
            db.add(notification)
            db.commit()
        
        return {"status": "sent", "notification_id": notification_id, "channel": "email"}
        
    except Exception as e:
        self.retry(exc=e, countdown=60, max_retries=3)

@celery_app.task(bind=True)
def send_slack_notification(self, message, channel="#general"):
    """Send Slack notification (mock implementation)"""
    try:
        # In production, integrate with Slack API
        time.sleep(0.3)  # Simulate API call delay
        
        notification_id = f"slack_{int(time.time())}"
        
        with SessionLocal() as db:
            notification = Notification(
                title="Slack Message",
                message=message,
                channel="slack",
                recipient=channel,
                status="sent",
                meta_data={"notification_id": notification_id, "slack_channel": channel}
            )
            db.add(notification)
            db.commit()
        
        return {"status": "sent", "notification_id": notification_id, "channel": "slack"}
        
    except Exception as e:
        self.retry(exc=e, countdown=30, max_retries=3)

@celery_app.task(bind=True)
def send_webhook_notification(self, url, payload):
    """Send webhook notification"""
    try:
        import httpx
        
        with httpx.Client() as client:
            response = client.post(url, json=payload, timeout=10.0)
            response.raise_for_status()
        
        notification_id = f"webhook_{int(time.time())}"
        
        with SessionLocal() as db:
            notification = Notification(
                title="Webhook Alert",
                message=json.dumps(payload),
                channel="webhook",
                recipient=url,
                status="sent",
                meta_data={"notification_id": notification_id, "response_status": response.status_code}
            )
            db.add(notification)
            db.commit()
        
        return {"status": "sent", "notification_id": notification_id, "channel": "webhook"}
        
    except Exception as e:
        self.retry(exc=e, countdown=45, max_retries=3)
