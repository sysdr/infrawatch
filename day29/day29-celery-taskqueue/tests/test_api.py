import pytest
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

class TestAPI:
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['service'] == 'celery-task-queue'

    def test_metrics_task_creation(self, client):
        """Test metrics collection task creation"""
        response = client.post('/api/tasks/metrics/start')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'task_id' in data
        assert data['status'] == 'started'
        assert data['queue'] == 'metrics.high'

    def test_data_processing_task_creation(self, client):
        """Test data processing task creation"""
        payload = {'batch': [1, 2, 3, 4, 5]}
        response = client.post('/api/tasks/data/process', 
                             data=json.dumps(payload),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'task_id' in data
        assert data['queue'] == 'metrics.normal'
        assert data['batch_size'] == 5

    def test_notification_task_creation(self, client):
        """Test notification task creation"""
        payload = {'message': 'Test message', 'priority': 'urgent'}
        response = client.post('/api/tasks/notification/send',
                             data=json.dumps(payload),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'task_id' in data
        assert data['queue'] == 'notifications.urgent'

    def test_report_generation_task_creation(self, client):
        """Test report generation task creation"""
        payload = {'type': 'monthly_report', 'filters': {'month': 'january'}}
        response = client.post('/api/tasks/report/generate',
                             data=json.dumps(payload),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'task_id' in data
        assert data['queue'] == 'reports.background'

    def test_worker_stats_endpoint(self, client):
        """Test worker statistics endpoint"""
        response = client.get('/api/workers/stats')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'queue_lengths' in data
        assert 'active_workers' in data
