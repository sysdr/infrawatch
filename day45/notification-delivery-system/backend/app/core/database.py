from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import os

# Use SQLite for development if PostgreSQL not available
database_url = os.getenv("DATABASE_URL", "sqlite:///./notification_delivery.db")
if database_url.startswith("postgresql"):
    engine = create_engine(database_url)
else:
    engine = create_engine(database_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
