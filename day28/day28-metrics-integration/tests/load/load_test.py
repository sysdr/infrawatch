from locust import HttpUser, task, between
import json
import random
import time

class MetricsUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Called when a user starts"""
        self.metric_names = [
            "cpu_usage", "memory_usage", "disk_io", "network_latency",
            "response_time", "error_rate", "throughput", "queue_size"
        ]
        self.sources = [
            "web-server-01", "web-server-02", "api-server-01", 
            "database-01", "cache-server-01", "worker-01"
        ]
    
    @task(3)
    def create_single_metric(self):
        """Create a single metric - most common operation"""
        metric = {
            "name": random.choice(self.metric_names),
            "value": round(random.uniform(0, 100), 2),
            "source": random.choice(self.sources),
            "tags": {
                "environment": random.choice(["prod", "staging", "dev"]),
                "region": random.choice(["us-east", "us-west", "eu-central"])
            }
        }
        
        with self.client.post("/api/v1/metrics", json=metric, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to create metric: {response.status_code}")
    
    @task(1)
    def create_batch_metrics(self):
        """Create batch of metrics"""
        batch_size = random.randint(5, 20)
        metrics = []
        
        for _ in range(batch_size):
            metrics.append({
                "name": random.choice(self.metric_names),
                "value": round(random.uniform(0, 100), 2),
                "source": random.choice(self.sources),
                "tags": {
                    "environment": random.choice(["prod", "staging"]),
                    "batch": str(int(time.time()))
                }
            })
        
        with self.client.post("/api/v1/metrics/batch", 
                            json={"metrics": metrics}, 
                            catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to create batch: {response.status_code}")
    
    @task(2)
    def query_metrics(self):
        """Query metrics - dashboard refresh"""
        params = {
            "limit": random.randint(50, 200),
            "offset": 0
        }
        
        # Sometimes filter by specific metric or source
        if random.random() < 0.3:
            params["name"] = random.choice(self.metric_names)
        
        if random.random() < 0.3:
            params["source"] = random.choice(self.sources)
        
        with self.client.get("/api/v1/metrics", params=params, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to query metrics: {response.status_code}")
    
    @task(2)
    def get_realtime_metrics(self):
        """Get realtime metrics from cache"""
        with self.client.get("/api/v1/metrics/realtime", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get realtime metrics: {response.status_code}")
    
    @task(1)
    def get_metric_summary(self):
        """Get metric summary statistics"""
        metric_name = random.choice(self.metric_names)
        hours = random.choice([1, 6, 24, 72])
        
        with self.client.get(f"/api/v1/metrics/{metric_name}/summary", 
                           params={"hours": hours},
                           catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get summary: {response.status_code}")
    
    @task(1)
    def health_check(self):
        """Health check - monitoring"""
        with self.client.get("/api/v1/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")

class DashboardUser(HttpUser):
    """Simulates dashboard users with SSE connections"""
    wait_time = between(10, 30)  # Dashboard users refresh less frequently
    
    @task
    def simulate_dashboard_usage(self):
        """Simulate typical dashboard user behavior"""
        # Check health
        self.client.get("/api/v1/health")
        
        # Get realtime metrics
        self.client.get("/api/v1/metrics/realtime")
        
        # Query some historical data
        self.client.get("/api/v1/metrics", params={"limit": 100})
        
        # Get a few metric summaries
        for metric in ["cpu_usage", "memory_usage", "response_time"]:
            self.client.get(f"/api/v1/metrics/{metric}/summary")
