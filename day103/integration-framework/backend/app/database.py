from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./integration.db")
opts = {"pool_pre_ping": True} if "postgresql" in DATABASE_URL else {"connect_args": {"check_same_thread": False}}
engine = create_engine(DATABASE_URL, **opts)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from app.models import Base
    Base.metadata.create_all(bind=engine)
