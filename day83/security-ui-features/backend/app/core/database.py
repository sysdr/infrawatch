from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError, DisconnectionError
import os

# Database URL - should be set via environment variable
# For local development, set DATABASE_URL in .env file
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost:5432/securitydb")

# Try to create engine, but handle connection errors gracefully
DB_AVAILABLE = False
engine = None
SessionLocal = None

try:
    engine = create_engine(
        DATABASE_URL, 
        pool_pre_ping=True, 
        pool_size=10, 
        max_overflow=20,
        connect_args={"connect_timeout": 2}
    )
    # Test connection
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        DB_AVAILABLE = True
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    except Exception as conn_e:
        print(f"Warning: Could not connect to database: {conn_e}")
        print("Application will run in mock data mode.")
        DB_AVAILABLE = False
except Exception as e:
    print(f"Warning: Database not available: {e}")
    print("Application will run in mock data mode.")
    DB_AVAILABLE = False
    engine = None
Base = declarative_base()

def get_db():
    """Get database session, returns None if database is unavailable"""
    if not DB_AVAILABLE or not SessionLocal:
        yield None
        return
    
    db = SessionLocal()
    try:
        # Test connection
        db.execute("SELECT 1")
        yield db
    except (OperationalError, DisconnectionError) as e:
        print(f"Database connection error: {e}")
        db.close()
        yield None
    except Exception as e:
        print(f"Database error: {e}")
        db.close()
        yield None
    finally:
        if db:
            try:
                db.close()
            except:
                pass
