from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import alert_router
from .models.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Alert Query & Management API",
    description="Advanced alert querying and management system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(alert_router)

@app.get("/")
async def root():
    return {"message": "Alert Query & Management System", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
