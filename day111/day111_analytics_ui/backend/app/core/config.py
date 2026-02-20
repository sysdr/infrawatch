from pydantic_settings import BaseSettings
from pydantic import model_validator
from functools import lru_cache

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://analytics:analytics_pass@localhost:5432/analytics_db"
    REDIS_URL: str = "redis://localhost:6379"
    SECRET_KEY: str = ""  # Set via .env or env; do not commit real values
    ENVIRONMENT: str = "development"

    @model_validator(mode="after")
    def require_secret_key(self):
        if not (self.SECRET_KEY and self.SECRET_KEY.strip()):
            raise ValueError("SECRET_KEY must be set in .env or environment")
        return self
    MODEL_DIR: str = "models"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
