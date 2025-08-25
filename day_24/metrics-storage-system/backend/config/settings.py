import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
    INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "dev-token-12345")
    INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "metrics-org")
    INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "metrics-bucket")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Compression settings
    COMPRESSION_ENABLED = True
    COMPRESSION_ALGORITHM = "gzip"
    COMPRESSION_LEVEL = 6
    
    # Partitioning settings
    PARTITION_SIZE_HOURS = 24
    HOT_DATA_RETENTION_HOURS = 72
    WARM_DATA_RETENTION_DAYS = 30
    COLD_DATA_RETENTION_DAYS = 365
    
    # Backup settings
    BACKUP_ENABLED = True
    BACKUP_INTERVAL_HOURS = 1
    BACKUP_RETENTION_DAYS = 7
    BACKUP_PATH = "./backup"

settings = Settings()
