from locust import HttpUser, task, between, events
import json
import time
import random

class DashboardUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Called when a user starts"""
        self.client_id = f"client-{time.time()}-{random.randint(1000, 9999)}"
        
    @task(10)
    def get_metric_history(self):
        """Simulate fetching historical metrics"""
        with self.client.get(
            "/api/metrics/history?limit=1000",
            catch_response=True,
            name="Get Metric History"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if len(data['metrics']) > 0:
                    response.success()
                else:
                    response.failure("No metrics returned")
                    
    @task(5)
    def get_performance_stats(self):
        """Simulate fetching performance stats"""
        with self.client.get(
            "/api/performance/stats",
            catch_response=True,
            name="Get Performance Stats"
        ) as response:
            if response.status_code == 200:
                response.success()
                
    @task(1)
    def health_check(self):
        """Periodic health check"""
        self.client.get("/api/health")

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("Performance test starting...")
    
@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("Performance test completed!")
    print(f"Total requests: {environment.stats.total.num_requests}")
    print(f"Total failures: {environment.stats.total.num_failures}")
    print(f"Average response time: {environment.stats.total.avg_response_time}ms")
    print(f"RPS: {environment.stats.total.total_rps}")
