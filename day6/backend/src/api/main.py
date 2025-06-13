from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.database import get_database_session
from src.models.log_event import LogEvent, LogLevel
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class LogEventCreate(BaseModel):
    message: str
    level: LogLevel = LogLevel.INFO
    source: Optional[str] = None
    metadata: Optional[str] = None

class LogEventResponse(BaseModel):
    id: int
    message: str
    level: LogLevel
    timestamp: datetime
    source: Optional[str]
    metadata: Optional[str]
    
    class Config:
        from_attributes = True

def create_app() -> FastAPI:
    app = FastAPI(title="Log Processing System", version="1.0.0")
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "log-processor"}
    
    @app.post("/logs", response_model=LogEventResponse)
    async def create_log_event(
        log_data: LogEventCreate,
        session: AsyncSession = Depends(get_database_session)
    ):
        """Create a new log event."""
        event = LogEvent(**log_data.dict())
        session.add(event)
        await session.commit()
        await session.refresh(event)
        return event
    
    @app.get("/logs", response_model=List[LogEventResponse])
    async def get_log_events(
        limit: int = 100,
        level: Optional[LogLevel] = None,
        session: AsyncSession = Depends(get_database_session)
    ):
        """Retrieve log events with optional filtering."""
        query = select(LogEvent).limit(limit).order_by(LogEvent.timestamp.desc())
        
        if level:
            query = query.where(LogEvent.level == level)
        
        result = await session.execute(query)
        return result.scalars().all()
    
    return app

if __name__ == "__main__":
    import uvicorn
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
