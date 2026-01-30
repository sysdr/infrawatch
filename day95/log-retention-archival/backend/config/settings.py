from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET_HOT: str
    MINIO_BUCKET_WARM: str
    MINIO_BUCKET_COLD: str
    HOT_RETENTION_DAYS: int = 7
    WARM_RETENTION_DAYS: int = 90
    COLD_RETENTION_DAYS: int = 2555
    COMPRESSION_ALGORITHM: str = "gzip"
    BATCH_SIZE: int = 10000
    ARCHIVAL_WORKERS: int = 4
    
    class Config:
        env_file = ".env"

settings = Settings()
