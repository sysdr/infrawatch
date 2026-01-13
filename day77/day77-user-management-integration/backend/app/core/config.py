from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/user_management"
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "CHANGE_THIS_IN_PRODUCTION_MIN_32_CHARS"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()
