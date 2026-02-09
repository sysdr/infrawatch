from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./scheduler.db")
_engine_opts = {"pool_pre_ping": True} if "postgresql" in DATABASE_URL else {"connect_args": {"check_same_thread": False}}
engine = create_engine(DATABASE_URL, **_engine_opts)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from app.models import Base, ResourcePool
    Base.metadata.create_all(bind=engine)
    
    # Initialize resource pools
    db = SessionLocal()
    try:
        if not db.query(ResourcePool).filter_by(resource_type="cpu").first():
            db.add(ResourcePool(resource_type="cpu", total_capacity=8.0))
        if not db.query(ResourcePool).filter_by(resource_type="memory").first():
            db.add(ResourcePool(resource_type="memory", total_capacity=16384.0))  # 16GB in MB
        db.commit()
    finally:
        db.close()
