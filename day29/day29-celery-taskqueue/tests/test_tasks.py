import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.tasks import collect_metrics, process_data, send_notification, generate_report
from app.celery_app import celery_app

class TestCeleryTasks:
    def test_collect_metrics_task_signature(self):
        """Test that collect_metrics task is properly registered"""
        assert 'app.tasks.collect_metrics' in celery_app.tasks
        
    def test_process_data_task_signature(self):
        """Test that process_data task is properly registered"""
        assert 'app.tasks.process_data' in celery_app.tasks
        
    def test_send_notification_task_signature(self):
        """Test that send_notification task is properly registered"""  
        assert 'app.tasks.send_notification' in celery_app.tasks
        
    def test_generate_report_task_signature(self):
        """Test that generate_report task is properly registered"""
        assert 'app.tasks.generate_report' in celery_app.tasks

    def test_task_routing_configuration(self):
        """Test that task routing is properly configured"""
        routes = celery_app.conf.task_routes
        assert routes['app.tasks.collect_metrics']['queue'] == 'metrics.high'
        assert routes['app.tasks.generate_report']['queue'] == 'reports.background'
        assert routes['app.tasks.send_notification']['queue'] == 'notifications.urgent'
        assert routes['app.tasks.process_data']['queue'] == 'metrics.normal'

    def test_celery_configuration(self):
        """Test Celery configuration settings"""
        assert celery_app.conf.task_serializer == 'json'
        assert celery_app.conf.result_serializer == 'json'
        assert celery_app.conf.task_acks_late == True
        assert celery_app.conf.worker_prefetch_multiplier == 1
