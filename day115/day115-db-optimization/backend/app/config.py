from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    primary_db_url: str = "postgresql://admin:admin_pass@localhost:5432/dbopt_dev"
    replica_db_url: str = ""  # Empty means use primary as fallback
    lag_threshold_ms: float = 500.0
    app_name: str = "DB Optimizer"
    debug: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
