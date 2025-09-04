from flask import Blueprint, jsonify, request
from app.tasks import collect_metrics, process_data, send_notification, generate_report, cleanup_old_results
from app.celery_app import celery_app
import redis
import json

main_bp = Blueprint('main', __name__)
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

@main_bp.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'celery-task-queue'})

@main_bp.route('/api/tasks/metrics/start', methods=['POST'])
def start_metrics_collection():
    """Start metrics collection task"""
    task = collect_metrics.delay()
    return jsonify({
        'task_id': task.id,
        'status': 'started',
        'queue': 'metrics.high'
    })

@main_bp.route('/api/tasks/data/process', methods=['POST'])
def process_data_batch():
    """Process data batch"""
    data = request.get_json()
    batch = data.get('batch', list(range(10)))  # Default batch
    
    task = process_data.delay(batch)
    return jsonify({
        'task_id': task.id,
        'status': 'started',
        'queue': 'metrics.normal',
        'batch_size': len(batch)
    })

@main_bp.route('/api/tasks/notification/send', methods=['POST'])
def send_notification_task():
    """Send notification"""
    data = request.get_json()
    message = data.get('message', 'Test notification')
    priority = data.get('priority', 'normal')
    
    task = send_notification.delay(message, priority)
    return jsonify({
        'task_id': task.id,
        'status': 'started',
        'queue': 'notifications.urgent'
    })

@main_bp.route('/api/tasks/report/generate', methods=['POST'])
def generate_report_task():
    """Generate report"""
    data = request.get_json()
    report_type = data.get('type', 'metrics_summary')
    filters = data.get('filters', {})
    
    task = generate_report.delay(report_type, filters)
    return jsonify({
        'task_id': task.id,
        'status': 'started',
        'queue': 'reports.background'
    })

@main_bp.route('/api/tasks/<task_id>/status', methods=['GET'])
def get_task_status(task_id):
    """Get task status"""
    task = celery_app.AsyncResult(task_id)
    
    if task.state == 'PENDING':
        response = {
            'task_id': task_id,
            'state': task.state,
            'status': 'Task is waiting to be processed'
        }
    elif task.state == 'PROGRESS':
        response = {
            'task_id': task_id,
            'state': task.state,
            'progress': task.info
        }
    else:
        response = {
            'task_id': task_id,
            'state': task.state,
            'result': task.info
        }
        
    return jsonify(response)

@main_bp.route('/api/workers/stats', methods=['GET'])
def get_worker_stats():
    """Get worker statistics"""
    try:
        inspect = celery_app.control.inspect()
        
        # Get active workers
        active_workers = inspect.active() or {}
        registered_tasks = inspect.registered() or {}
        worker_stats = inspect.stats() or {}
        
        # Get queue lengths
        queue_lengths = {}
        for queue in ['metrics.high', 'metrics.normal', 'notifications.urgent', 'reports.background', 'default']:
            try:
                length = redis_client.llen(queue)
                queue_lengths[queue] = length
            except:
                queue_lengths[queue] = 0
        
        return jsonify({
            'active_workers': len(active_workers),
            'worker_details': active_workers,
            'registered_tasks': registered_tasks,
            'worker_stats': worker_stats,
            'queue_lengths': queue_lengths
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/tasks/cleanup', methods=['POST'])
def start_cleanup():
    """Start cleanup task"""
    task = cleanup_old_results.delay()
    return jsonify({
        'task_id': task.id,
        'status': 'started',
        'queue': 'default'
    })
