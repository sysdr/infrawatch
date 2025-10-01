from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/alertdb"
    REDIS_URL: str = "redis://localhost:6379"
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Alert Evaluation Engine"
    EVALUATION_INTERVAL: int = 30  # seconds
    MAX_CONCURRENT_EVALUATIONS: int = 100
    ANOMALY_DETECTION_WINDOW: int = 3600  # 1 hour in seconds
    
    class Config:
        case_sensitive = True

settings = Settings()
