import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import redis.asyncio as redis
from typing import AsyncGenerator

# Database configuration
def get_database_url():
    return os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost/metrics_db")

def get_redis_url():
    return os.getenv("REDIS_URL", "redis://localhost:6379/0")

# SQLAlchemy setup
def get_engine():
    return create_engine(
        get_database_url(),
        poolclass=StaticPool,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False
    )

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Redis setup
redis_client = None

async def get_redis() -> redis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(get_redis_url(), decode_responses=True)
    return redis_client

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    """Initialize database tables"""
    from app.models.metric import Base
    Base.metadata.create_all(bind=engine)
    
    # Add sample data for testing
    from app.services.sample_data import create_sample_metrics
    await create_sample_metrics()

async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.close()
