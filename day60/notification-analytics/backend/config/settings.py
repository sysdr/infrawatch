from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://analytics:analytics123@localhost:5432/analytics_db"
    REDIS_URL: str = "redis://localhost:6379/0"
    ANOMALY_Z_SCORE_THRESHOLD: float = 3.0
    CORRELATION_THRESHOLD: float = 0.7
    CACHE_TTL: int = 300

settings = Settings()
