from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Automation Integration Engine"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database (SQLite for local/demo when PostgreSQL not available)
    DATABASE_URL: str = "sqlite+aiosqlite:///./automation.db"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Security - set SECRET_KEY in environment for production; dev placeholder only
    SECRET_KEY: str = "dev-only-set-SECRET_KEY-in-env-for-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Execution settings
    MAX_CONCURRENT_EXECUTIONS: int = 10
    MAX_RETRY_ATTEMPTS: int = 3
    EXECUTION_TIMEOUT_SECONDS: int = 300
    
    # Performance targets
    THROUGHPUT_TARGET: int = 10000  # executions per second
    
    class Config:
        case_sensitive = True

settings = Settings()
