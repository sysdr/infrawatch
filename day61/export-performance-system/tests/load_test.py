from locust import HttpUser, task, between
import random

class ExportPerformanceUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def export_notifications(self):
        """Test export with various parameters"""
        params = {
            'user_id': f'user{random.randint(0, 99)}',
            'format': random.choice(['json', 'csv']),
            'use_cache': True
        }
        self.client.post("/api/exports/notifications", params=params)
    
    @task(1)
    def get_metrics(self):
        """Test metrics endpoint"""
        self.client.get("/api/performance/metrics")
    
    @task(1)
    def get_cache_stats(self):
        """Test cache stats"""
        self.client.get("/api/cache/stats")
