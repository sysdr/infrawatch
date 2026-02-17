from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import reports, templates, schedules, distribution, dashboard
from app.models.database import engine, Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Advanced Reporting System", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(templates.router, prefix="/api/templates", tags=["templates"])
app.include_router(schedules.router, prefix="/api/schedules", tags=["schedules"])
app.include_router(distribution.router, prefix="/api/distribution", tags=["distribution"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])

@app.get("/")
async def root():
    return {"message": "Advanced Reporting System API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
