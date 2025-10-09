from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "Alert Query Management"
    debug: bool = True
    database_url: str = "postgresql://alerts:password@localhost:5432/alertsdb"
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = "your-secret-key-change-in-production"
    
    class Config:
        env_file = ".env"

settings = Settings()
