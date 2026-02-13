from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./ml_pipeline.db"
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6406")
    use_redis: bool = False
    model_retrain_interval: int = 300   # seconds
    anomaly_window: int = 60            # data points
    forecast_steps: int = 24
    contamination: float = 0.05
    n_clusters: int = 3
    cors_origins: list[str] = ["http://localhost:3106", "http://localhost:5173"]

settings = Settings()
