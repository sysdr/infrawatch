import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.metrics import Base

# Use Docker service names when running in Docker, localhost when running locally
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://metrics_user:metrics_pass@localhost:5432/metrics_db"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise
