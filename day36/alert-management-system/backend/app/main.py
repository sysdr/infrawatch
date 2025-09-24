from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.alert_rules import router as alert_router
from .models.base import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Alert Management System", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(alert_router)

@app.get("/")
async def root():
    return {"message": "Alert Management System API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2025-01-01T00:00:00Z"}
