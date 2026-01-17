"""Performance tests"""
from locust import HttpUser, task, between

class SecurityMonitoringUser(HttpUser):
    wait_time = between(1, 2)
    
    @task
    def get_summary(self):
        self.client.get("/api/analytics/summary")
    
    @task
    def get_threats(self):
        self.client.get("/api/threats/active")
    
    @task
    def get_events(self):
        self.client.get("/api/events/recent")
