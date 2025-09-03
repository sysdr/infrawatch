from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/metrics_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # Metrics
    METRICS_BATCH_SIZE: int = 100
    METRICS_BATCH_INTERVAL: int = 30
    
    # Performance
    MAX_CONNECTIONS: int = 20
    POOL_SIZE: int = 5
    
    # Cache TTL
    REDIS_TTL: int = 300  # 5 minutes
    
    class Config:
        env_file = ".env"

settings = Settings()
