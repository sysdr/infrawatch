from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/usermgmt"
    )
    REDIS_URL: str = os.getenv(
        "REDIS_URL",
        "redis://localhost:6379/0"
    )
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        ""  # Must be set via environment variable in production
    )
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "300"))
    PERMISSION_CACHE_TTL: int = int(os.getenv("PERMISSION_CACHE_TTL", "300"))
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

# Validate SECRET_KEY is set in production
if not settings.SECRET_KEY:
    import warnings
    warnings.warn(
        "SECRET_KEY is not set. Please set it via environment variable or .env file.",
        UserWarning
    )
