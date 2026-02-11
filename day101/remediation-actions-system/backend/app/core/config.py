from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Remediation Actions System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str = "sqlite:///./remediation.db"
    REDIS_URL: str = "redis://localhost:6379"
    
    MAX_ACTIONS_PER_HOUR: int = 50
    DEFAULT_BLAST_RADIUS_LIMIT: int = 100
    ROLLBACK_RETENTION_DAYS: int = 7
    
    AUTO_APPROVE_RISK_THRESHOLD: float = 30.0
    CRITICAL_RISK_THRESHOLD: float = 80.0
    
    class Config:
        env_file = ".env"

settings = Settings()
