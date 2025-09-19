from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/metrics_db")

# Create engine
engine = create_engine(DATABASE_URL, echo=True)

# Create session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
