"""
Locust load test user journeys.
Run with: locust -f locustfiles/user_journeys.py --host=http://localhost:8117
"""
from locust import HttpUser, task, between, events
from faker import Faker
import random, json

fake = Faker()

class UserTeamJourney(HttpUser):
    wait_time = between(0.5, 2.0)
    host = "http://localhost:8117"

    def on_start(self):
        self.user_id = random.randint(1, 100)
        self.team_id = random.randint(1, 10)

    @task(4)
    def browse_users(self):
        page = random.randint(1, 5)
        self.client.get(f"/api/users?page={page}&limit=20", name="/api/users[paginated]")

    @task(3)
    def get_user_profile(self):
        uid = random.randint(1, 100)
        self.client.get(f"/api/users/{uid}", name="/api/users/{id}")

    @task(2)
    def browse_teams(self):
        self.client.get("/api/teams")

    @task(2)
    def get_team_detail(self):
        tid = random.randint(1, 10)
        self.client.get(f"/api/teams/{tid}", name="/api/teams/{id}")

    @task(1)
    def get_team_members(self):
        tid = random.randint(1, 5)
        self.client.get(f"/api/teams/{tid}/members", name="/api/teams/{id}/members")

    @task(1)
    def dashboard_stats(self):
        self.client.get("/api/dashboard/stats")

    @task(1)
    def update_user(self):
        self.client.put(
            f"/api/users/{self.user_id}",
            json={"name": fake.name()},
            name="/api/users/{id} [PUT]"
        )

    @task(1)
    def health_check(self):
        self.client.get("/api/health")


class AdminUser(HttpUser):
    """Simulates admin-level operations (heavier DB queries)."""
    wait_time = between(2.0, 5.0)
    weight = 1  # 1 admin per 3 regular users
    host = "http://localhost:8117"

    @task(3)
    def dashboard(self):
        self.client.get("/api/dashboard/stats")

    @task(2)
    def all_users(self):
        self.client.get("/api/users?page=1&limit=100", name="/api/users[admin-view]")

    @task(1)
    def all_teams(self):
        self.client.get("/api/teams")
