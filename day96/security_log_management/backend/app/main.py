from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import security, audit, incidents, compliance
from app.middleware.security_logger import SecurityLoggerMiddleware
from app.utils.database import engine, Base

app = FastAPI(title="Security Log Management System")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security logging middleware
app.add_middleware(SecurityLoggerMiddleware)

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(security.router, prefix="/api/security", tags=["security"])
app.include_router(audit.router, prefix="/api/audit", tags=["audit"])
app.include_router(incidents.router, prefix="/api/incidents", tags=["incidents"])
app.include_router(compliance.router, prefix="/api/compliance", tags=["compliance"])

@app.get("/")
def root():
    return {"message": "Security Log Management System API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
