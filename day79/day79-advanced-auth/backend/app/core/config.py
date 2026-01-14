from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@postgres:5432/authdb"
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    SECRET_KEY: str = os.getenv("SECRET_KEY", "CHANGE-THIS-IN-PRODUCTION-MIN-32-CHARACTERS-REQUIRED")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    class Config:
        env_file = ".env"

settings = Settings()
