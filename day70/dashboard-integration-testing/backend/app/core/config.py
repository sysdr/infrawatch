from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Dashboard Integration Testing"
    API_V1_STR: str = "/api/v1"
    REDIS_URL: str = "redis://localhost:6379"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/dashboard_test"  # Default for local dev, override with env var
    
    class Config:
        case_sensitive = True

settings = Settings()
