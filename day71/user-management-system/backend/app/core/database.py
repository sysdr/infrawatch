from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import os
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/user_management"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    try:
    db = SessionLocal()
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to create database session: {error_msg}")
        if "connection" in error_msg.lower() or "refused" in error_msg.lower():
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database service unavailable. Please ensure PostgreSQL is running on localhost:5432"
            )
        raise
    
    try:
        yield db
    except SQLAlchemyError as e:
        error_msg = str(e)
        logger.error(f"Database error: {error_msg}")
        db.rollback()
        if "connection" in error_msg.lower() or "refused" in error_msg.lower():
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database service unavailable. Please ensure PostgreSQL is running on localhost:5432"
            )
        raise
    except Exception as e:
        logger.error(f"Unexpected error in database session: {e}")
        db.rollback()
        raise
    finally:
        db.close()
