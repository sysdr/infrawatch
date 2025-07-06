from locust import HttpUser, task, between
import random

class AuthUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Setup user data for testing"""
        self.user_id = random.randint(1000, 9999)
        self.email = f"loadtest{self.user_id}@example.com"
        self.password = "LoadTest123!"
        self.first_name = "Load"
        self.last_name = "Test"
        
        # Register user for testing
        try:
            self.client.post("/api/auth/register", json={
                "email": self.email,
                "password": self.password,
                "first_name": self.first_name,
                "last_name": self.last_name
            })
        except:
            pass  # User might already exist
    
    @task(3)
    def login(self):
        """Test login performance"""
        self.client.post("/api/auth/login", json={
            "email": self.email,
            "password": self.password
        })
    
    @task(1)
    def register(self):
        """Test registration performance"""
        new_user_id = random.randint(10000, 99999)
        self.client.post("/api/auth/register", json={
            "email": f"newuser{new_user_id}@example.com",
            "password": "NewUser123!",
            "first_name": "New",
            "last_name": "User"
        })
    
    @task(2)
    def health_check(self):
        """Test health endpoint performance"""
        self.client.get("/api/health")
    
    @task(1)
    def profile_access(self):
        """Test protected endpoint performance"""
        # First login to get token
        response = self.client.post("/api/auth/login", json={
            "email": self.email,
            "password": self.password
        })
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            
            if token:
                # Access protected endpoint
                self.client.get("/api/auth/profile", headers={
                    "Authorization": f"Bearer {token}"
                })

class StressTestUser(HttpUser):
    wait_time = between(0.1, 0.5)  # Faster requests for stress testing
    
    @task(5)
    def rapid_login_attempts(self):
        """Test rapid login attempts to stress the system"""
        self.client.post("/api/auth/login", json={
            "email": f"stress{random.randint(1, 1000)}@example.com",
            "password": "wrong_password"
        })
    
    @task(3)
    def rapid_registration(self):
        """Test rapid registration attempts"""
        user_id = random.randint(100000, 999999)
        self.client.post("/api/auth/register", json={
            "email": f"stress{user_id}@example.com",
            "password": "StressTest123!",
            "first_name": "Stress",
            "last_name": "Test"
        })
    
    @task(2)
    def concurrent_health_checks(self):
        """Test concurrent health check requests"""
        self.client.get("/api/health")

class SecurityTestUser(HttpUser):
    wait_time = between(2, 5)  # Slower to avoid overwhelming
    
    @task(1)
    def test_weak_passwords(self):
        """Test weak password attempts"""
        weak_passwords = ["password", "12345678", "Password", "password123"]
        password = random.choice(weak_passwords)
        
        self.client.post("/api/auth/register", json={
            "email": f"security{random.randint(1, 1000)}@example.com",
            "password": password,
            "first_name": "Security",
            "last_name": "Test"
        })
    
    @task(1)
    def test_invalid_emails(self):
        """Test invalid email attempts"""
        invalid_emails = ["invalid-email", "@example.com", "user@", "user@.com"]
        email = random.choice(invalid_emails)
        
        self.client.post("/api/auth/register", json={
            "email": email,
            "password": "ValidPass123!",
            "first_name": "Security",
            "last_name": "Test"
        })
    
    @task(1)
    def test_sql_injection(self):
        """Test SQL injection attempts"""
        sql_attempts = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "admin'--",
            "test@example.com' UNION SELECT * FROM users--"
        ]
        attempt = random.choice(sql_attempts)
        
        self.client.post("/api/auth/register", json={
            "email": attempt,
            "password": "ValidPass123!",
            "first_name": "Security",
            "last_name": "Test"
        }) 