#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.celery_app import celery_app

if __name__ == '__main__':
    # Start Celery worker with specific queue configuration
    celery_app.worker_main([
        'worker',
        '--loglevel=info',
        '--queues=metrics.high,metrics.normal,notifications.urgent,reports.background,default',
        '--concurrency=4',
        '--max-tasks-per-child=1000'
    ])
