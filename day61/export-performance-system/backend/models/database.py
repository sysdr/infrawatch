from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, DateTime, Integer, JSON, Text
from datetime import datetime
from contextlib import asynccontextmanager
import os

# Database URL should be set via environment variable
# For local development: export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/export_performance"
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable must be set")

engine = create_async_engine(DATABASE_URL, pool_size=20, max_overflow=40, echo=False)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, index=True)
    type = Column(String)
    status = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    meta_data = Column(JSON, name='metadata')

class ExportJob(Base):
    __tablename__ = "export_jobs"
    
    id = Column(String, primary_key=True)
    user_id = Column(String)
    status = Column(String, index=True)
    query_params = Column(JSON)
    execution_time_ms = Column(Integer)
    row_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Insert sample data
    async with async_session_maker() as session:
        from sqlalchemy import select, func
        result = await session.execute(select(func.count()).select_from(Notification))
        count = result.scalar()
        
        if count == 0:
            import uuid
            notifications = []
            for i in range(10000):
                notifications.append(Notification(
                    id=str(uuid.uuid4()),
                    user_id=f"user{i % 100}",
                    type=["email", "sms", "push", "webhook"][i % 4],
                    status=["sent", "pending", "failed"][i % 3],
                    timestamp=datetime.utcnow(),
                    meta_data={"priority": i % 5, "retry_count": i % 3}
                ))
            
            session.add_all(notifications)
            await session.commit()

@asynccontextmanager
async def get_db():
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

async def close_db():
    await engine.dispose()
