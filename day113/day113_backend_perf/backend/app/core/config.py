from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://perf_user:perf_pass@localhost:5432/perf_db"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 5
    DB_POOL_RECYCLE: int = 1800
    DB_POOL_PRE_PING: bool = True
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_DEFAULT_TTL: int = 300
    CACHE_COLD_TTL: int = 30
    APP_NAME: str = "BackendPerfDemo"
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()
