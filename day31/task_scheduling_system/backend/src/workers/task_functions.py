import asyncio
import psutil
import json
from datetime import datetime
import random

async def collect_system_metrics():
    """Collect system metrics"""
    await asyncio.sleep(1)  # Simulate work
    
    metrics = {
        "timestamp": datetime.utcnow().isoformat(),
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
        "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
    }
    
    return metrics

async def generate_usage_report():
    """Generate usage report"""
    await asyncio.sleep(2)  # Simulate work
    
    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "report_type": "usage_summary",
        "data_points": random.randint(100, 1000),
        "processing_time": random.uniform(1.5, 3.0)
    }
    
    return report

async def cleanup_old_logs():
    """Clean up old log files"""
    await asyncio.sleep(0.5)  # Simulate work
    
    result = {
        "timestamp": datetime.utcnow().isoformat(),
        "files_cleaned": random.randint(5, 50),
        "space_freed_mb": random.randint(100, 1000)
    }
    
    return result

async def send_notifications():
    """Send notifications"""
    await asyncio.sleep(1)  # Simulate work
    
    result = {
        "timestamp": datetime.utcnow().isoformat(),
        "notifications_sent": random.randint(1, 10),
        "success_rate": random.uniform(0.8, 1.0)
    }
    
    return result

async def database_backup():
    """Perform database backup"""
    await asyncio.sleep(3)  # Simulate work
    
    result = {
        "timestamp": datetime.utcnow().isoformat(),
        "backup_size_mb": random.randint(500, 5000),
        "backup_duration_seconds": random.uniform(2.0, 5.0),
        "backup_location": "/backups/db_backup.sql"
    }
    
    return result

# Task functions registry
task_functions = {
    'collect_system_metrics': collect_system_metrics,
    'generate_usage_report': generate_usage_report,
    'cleanup_old_logs': cleanup_old_logs,
    'send_notifications': send_notifications,
    'database_backup': database_backup
}
