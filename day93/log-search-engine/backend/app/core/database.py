from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
import redis
from typing import Generator

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=40
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

# Enable PostgreSQL extensions on connection
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    try:
        cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
        cursor.execute("CREATE EXTENSION IF NOT EXISTS btree_gin;")
        dbapi_conn.commit()
    finally:
        cursor.close()

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_redis():
    return redis_client
