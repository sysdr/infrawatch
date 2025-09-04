from app.celery_app import celery_app
import time
import random
import json
from datetime import datetime
import requests
import psutil

@celery_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
def collect_metrics(self):
    """Collect system metrics with retry logic"""
    try:
        # Simulate metric collection
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        disk_info = psutil.disk_usage('/')
        
        metrics = {
            'timestamp': datetime.utcnow().isoformat(),
            'cpu_percent': cpu_percent,
            'memory_percent': memory_info.percent,
            'disk_percent': (disk_info.used / disk_info.total) * 100,
            'worker_id': self.request.id
        }
        
        # Simulate occasional failures for demonstration
        if random.random() < 0.1:
            raise Exception("Simulated metric collection failure")
            
        print(f"✅ Metrics collected: {json.dumps(metrics, indent=2)}")
        return metrics
        
    except Exception as exc:
        print(f"❌ Metrics collection failed: {exc}")
        raise self.retry(exc=exc)

@celery_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 5, 'countdown': 30})
def process_data(self, data_batch):
    """Process data batch with exponential backoff retry"""
    try:
        # Simulate data processing
        processed_count = 0
        for item in data_batch:
            # Simulate processing time
            time.sleep(0.1)
            processed_count += 1
            
            # Update task progress
            self.update_state(
                state='PROGRESS',
                meta={'processed': processed_count, 'total': len(data_batch)}
            )
        
        result = {
            'processed_items': processed_count,
            'batch_size': len(data_batch),
            'completion_time': datetime.utcnow().isoformat()
        }
        
        print(f"✅ Data processing completed: {json.dumps(result)}")
        return result
        
    except Exception as exc:
        print(f"❌ Data processing failed: {exc}")
        raise self.retry(exc=exc, countdown=min(2 ** self.request.retries, 300))

@celery_app.task(bind=True)
def send_notification(self, message, priority='normal'):
    """Send notification with priority handling"""
    try:
        notification = {
            'message': message,
            'priority': priority,
            'sent_at': datetime.utcnow().isoformat(),
            'task_id': self.request.id
        }
        
        # Simulate notification sending
        time.sleep(0.5)
        print(f"📧 Notification sent: {json.dumps(notification)}")
        return notification
        
    except Exception as exc:
        print(f"❌ Notification failed: {exc}")
        raise exc

@celery_app.task(bind=True)
def generate_report(self, report_type, filters=None):
    """Generate report in background"""
    try:
        # Simulate report generation with progress updates
        total_steps = 10
        for step in range(total_steps):
            time.sleep(2)  # Simulate work
            self.update_state(
                state='PROGRESS',
                meta={'step': step + 1, 'total': total_steps, 'message': f'Processing step {step + 1}'}
            )
        
        report = {
            'type': report_type,
            'filters': filters or {},
            'generated_at': datetime.utcnow().isoformat(),
            'size': random.randint(1000, 50000),
            'status': 'completed'
        }
        
        print(f"📊 Report generated: {json.dumps(report)}")
        return report
        
    except Exception as exc:
        print(f"❌ Report generation failed: {exc}")
        raise exc

@celery_app.task
def cleanup_old_results():
    """Cleanup old task results - maintenance task"""
    try:
        # This would typically clean up old Redis keys
        cleanup_count = random.randint(50, 200)
        print(f"🧹 Cleaned up {cleanup_count} old task results")
        return {'cleaned_items': cleanup_count}
    except Exception as exc:
        print(f"❌ Cleanup failed: {exc}")
        raise exc
