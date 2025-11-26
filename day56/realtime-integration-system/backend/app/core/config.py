from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Real-time Integration System"
    DEBUG: bool = True
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # WebSocket
    WS_MAX_CONNECTIONS: int = 10000
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_MESSAGE_BATCH_SIZE: int = 10
    WS_MESSAGE_BATCH_TIMEOUT: float = 0.05
    
    # Circuit Breaker
    CB_FAILURE_THRESHOLD: int = 5
    CB_RECOVERY_TIMEOUT: int = 30
    CB_SUCCESS_THRESHOLD: int = 2
    
    # Reconnection
    RECONNECT_MAX_ATTEMPTS: int = 10
    RECONNECT_BASE_DELAY: float = 1.0
    RECONNECT_MAX_DELAY: float = 30.0
    
    # Performance
    LATENCY_BUDGET_MS: int = 50
    MESSAGE_QUEUE_SIZE: int = 1000
    
    class Config:
        env_file = ".env"

settings = Settings()
