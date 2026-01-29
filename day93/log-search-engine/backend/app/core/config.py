from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Log Search Engine"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/logsearch"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    SECRET_KEY: str = ""  # Set via SECRET_KEY env var - required for JWT in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    CACHE_TTL: int = 60
    MAX_SEARCH_RESULTS: int = 1000
    
    class Config:
        case_sensitive = True

settings = Settings()
