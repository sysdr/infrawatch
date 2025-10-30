from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from config.database import get_db
from api import preferences, users, notifications
from models.base import Base
from config.database import engine

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Notification Preferences API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(preferences.router, prefix="/api/v1/preferences", tags=["preferences"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["notifications"])

@app.get("/")
async def root():
    return {"message": "Notification Preferences API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
