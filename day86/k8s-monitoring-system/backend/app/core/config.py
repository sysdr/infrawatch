from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "K8s Monitoring System"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/k8s_monitor"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Kubernetes
    K8S_IN_CLUSTER: bool = False
    K8S_CONFIG_FILE: Optional[str] = None
    
    # Monitoring
    METRICS_INTERVAL: int = 15  # seconds
    HEALTH_CHECK_INTERVAL: int = 5  # seconds
    
    class Config:
        env_file = ".env"

settings = Settings()
