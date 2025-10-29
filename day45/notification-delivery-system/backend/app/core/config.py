from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://user:password@localhost/notification_delivery"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Queue settings
    max_queue_size: int = 10000
    worker_count: int = 4
    batch_size: int = 100
    
    # Retry settings
    max_retry_attempts: int = 3
    retry_base_delay: float = 1.0
    retry_max_delay: float = 300.0
    
    # Rate limiting
    default_rate_limit: int = 10  # per minute
    rate_limit_window: int = 60   # seconds
    
    # Notification channels
    email_enabled: bool = True
    sms_enabled: bool = True
    push_enabled: bool = True
    
    # External services
    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    
    class Config:
        env_file = ".env"

settings = Settings()
