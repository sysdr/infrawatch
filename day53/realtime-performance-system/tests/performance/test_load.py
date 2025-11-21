from locust import HttpUser, task, between
import json
import random

class NotificationUser(HttpUser):
    wait_time = between(0.1, 0.5)
    
    def on_start(self):
        self.user_id = f"user_{random.randint(1, 10000)}"
    
    @task(3)
    def create_notification(self):
        self.client.post("/api/notifications/", json={
            "user_id": self.user_id,
            "message": f"Load test message {random.randint(1, 1000)}",
            "priority": random.choice(["critical", "normal", "low"]),
            "notification_type": "info"
        })
    
    @task(1)
    def get_metrics(self):
        self.client.get("/api/metrics/current")
    
    @task(1)
    def check_health(self):
        self.client.get("/health")
