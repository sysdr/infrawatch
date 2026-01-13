from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
import os

# Use SQLite for development if PostgreSQL is not available
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Try PostgreSQL first, fallback to SQLite
    # Get database credentials from environment variables
    db_user = os.getenv("DB_USER", "security")
    db_password = os.getenv("DB_PASSWORD", "")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "security_db")
    
    if db_password:
        try:
            import psycopg2
            psycopg2.connect(f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")
            DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        except:
            DATABASE_URL = "sqlite:///./security_assessment.db"
    else:
        DATABASE_URL = "sqlite:///./security_assessment.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
