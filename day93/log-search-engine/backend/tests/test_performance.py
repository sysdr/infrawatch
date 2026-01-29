from locust import HttpUser, task, between
import random

QUERIES = [
    "level:error",
    "service:api",
    "level:error AND service:api",
    "message:*timeout*",
    "level:error OR level:critical"
]

class SearchUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def search(self):
        query = random.choice(QUERIES)
        self.client.get(f"/api/v1/search?q={query}&page=1&page_size=50")
    
    @task(1)
    def get_facets(self):
        query = random.choice(QUERIES)
        self.client.get(f"/api/v1/facets?q={query}")
    
    @task(1)
    def get_suggestions(self):
        self.client.get("/api/v1/suggestions?q=level:")
