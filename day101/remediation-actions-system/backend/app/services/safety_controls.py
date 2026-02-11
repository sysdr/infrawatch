from datetime import datetime
from typing import Optional

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

class SafetyControls:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = None
        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                self.redis_client.ping()
            except Exception:
                self.redis_client = None
    
    def check_rate_limit(self, max_per_hour: int = 50) -> bool:
        if not self.redis_client:
            return True
        try:
            key = f"rate_limit:actions:{datetime.utcnow().strftime('%Y-%m-%d-%H')}"
            current = self.redis_client.get(key)
            if current is None:
                self.redis_client.setex(key, 3600, 1)
                return True
            if int(current) >= max_per_hour:
                return False
            self.redis_client.incr(key)
            return True
        except Exception:
            return True
    
    def calculate_blast_radius(self, parameters: dict, template_max: int) -> int:
        affected_resources = 1
        for key, value in parameters.items():
            if isinstance(value, list):
                affected_resources = max(affected_resources, len(value))
            elif isinstance(value, str):
                if '/' in value or '-' in value:
                    if '/24' in value:
                        affected_resources = max(affected_resources, 256)
                    elif '/16' in value:
                        affected_resources = max(affected_resources, 65536)
        return min(affected_resources, template_max)
    
    def validate_blast_radius(self, calculated: int, template_max: int, global_max: int) -> tuple[bool, Optional[str]]:
        if calculated > template_max:
            return False, f"Blast radius {calculated} exceeds template limit {template_max}"
        if calculated > global_max:
            return False, f"Blast radius {calculated} exceeds global limit {global_max}"
        return True, None
    
    def calculate_risk_score(self, template_risk: str, blast_radius: int, parameters: dict) -> float:
        base_risk = {
            "low": 20.0,
            "medium": 50.0,
            "high": 75.0,
            "critical": 90.0
        }.get(template_risk, 50.0)
        blast_radius_multiplier = min(1.0 + (blast_radius / 100), 2.0)
        sensitive_multiplier = 1.0
        sensitive_params = ["database_credentials", "encryption_keys", "api_tokens", "shutdown", "delete"]
        for param_key in parameters.keys():
            if any(sensitive in str(param_key).lower() for sensitive in sensitive_params):
                sensitive_multiplier = 1.5
                break
        final_score = min(base_risk * blast_radius_multiplier * sensitive_multiplier, 100.0)
        return round(final_score, 2)

safety_controls = SafetyControls()
