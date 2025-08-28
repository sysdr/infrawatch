"""Development configuration"""

import os

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./metrics.db")

# Redis Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Aggregation Settings
AGGREGATION_WINDOW_SIZE = 300  # 5 minutes
MAX_MEMORY_POINTS = 10000
ROLLUP_INTERVAL = 60  # 1 minute

# API Settings
API_HOST = "0.0.0.0"
API_PORT = 8000
DEBUG = True

# CORS Settings
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# WebSocket Settings
WS_HEARTBEAT_INTERVAL = 30
WS_MAX_CONNECTIONS = 100

# Metrics Generation (for demo)
GENERATE_SAMPLE_METRICS = True
SAMPLE_METRICS_INTERVAL = 1  # seconds
