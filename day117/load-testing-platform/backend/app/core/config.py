from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "LoadTestingPlatform"
    backend_port: int = 8117
    target_base_url: str = "http://localhost:8117"
    db_url: str = "sqlite+aiosqlite:///./data/loadtest.db"
    max_workers: int = 4
    metrics_interval_seconds: int = 2

    class Config:
        env_file = ".env"

settings = Settings()
