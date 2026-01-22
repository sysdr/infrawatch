from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/cloudapi"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # AWS Configuration
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    
    # Collection intervals (seconds)
    EC2_COLLECTION_INTERVAL: int = 60
    RDS_COLLECTION_INTERVAL: int = 300
    S3_COLLECTION_INTERVAL: int = 900
    LAMBDA_COLLECTION_INTERVAL: int = 120
    
    # Cache TTLs (seconds)
    CACHE_TTL_EC2: int = 60
    CACHE_TTL_RDS: int = 300
    CACHE_TTL_S3: int = 900
    CACHE_TTL_COSTS: int = 300
    
    # Health monitoring
    HEALTH_CHECK_INTERVAL: int = 30
    HEALTH_SCORE_THRESHOLD_DEGRADED: int = 89
    HEALTH_SCORE_THRESHOLD_UNHEALTHY: int = 49
    
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
