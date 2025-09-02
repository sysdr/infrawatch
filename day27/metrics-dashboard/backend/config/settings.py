import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Metrics Dashboard"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database
    database_url: str = "sqlite:///./metrics.db"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # CORS
    allowed_origins: list = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"

settings = Settings()
