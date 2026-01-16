from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://apiuser:apipass123@localhost:5432/api_security_db"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Security
    secret_key: str = "dev-secret-key-change-in-production-32chars-minimum"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60
    
    # API Keys
    api_key_prefix: str = "sk_live"
    api_key_expiry_days: int = 90
    
    # Request Signing
    signature_max_age: int = 300  # 5 minutes
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
