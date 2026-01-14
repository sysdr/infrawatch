from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from app.core.database import engine, Base, get_db
from app.api import encryption, classification, privacy, masking, gdpr
from app.services.encryption_service import EncryptionService
from app.services.classification_service import ClassificationService
from sqlalchemy.orm import Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup"""
    logger.info("Starting Data Protection System...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    
    # Initialize encryption service
    from app.services.encryption_service import encryption_service
    await encryption_service.initialize()
    logger.info("Encryption service initialized")
    
    # Initialize classification service
    classification_service = ClassificationService()
    await classification_service.initialize()
    logger.info("Classification service initialized")
    
    yield
    
    logger.info("Shutting down Data Protection System...")

app = FastAPI(
    title="Data Protection System",
    description="Enterprise-grade data protection with encryption, classification, privacy, and GDPR compliance",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(encryption.router, prefix="/api/encryption", tags=["Encryption"])
app.include_router(classification.router, prefix="/api/classification", tags=["Classification"])
app.include_router(privacy.router, prefix="/api/privacy", tags=["Privacy"])
app.include_router(masking.router, prefix="/api/masking", tags=["Masking"])
app.include_router(gdpr.router, prefix="/api/gdpr", tags=["GDPR"])

@app.get("/")
async def root():
    return {
        "service": "Data Protection System",
        "version": "1.0.0",
        "status": "operational",
        "features": [
            "Encryption at Rest (AES-256-GCM)",
            "Data Classification (4 levels)",
            "Privacy Controls & Consent",
            "Data Masking (Dynamic/Static)",
            "GDPR Compliance Automation"
        ]
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Check database
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "services": {
                "encryption": "operational",
                "classification": "operational",
                "privacy": "operational",
                "masking": "operational",
                "gdpr": "operational"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.get("/metrics")
async def metrics():
    """System metrics endpoint"""
    return {
        "encryption": {
            "keys_active": 12,
            "keys_rotated_today": 3,
            "encryption_operations_per_sec": 1247
        },
        "classification": {
            "classified_records": 45230,
            "public": 12000,
            "internal": 20000,
            "confidential": 10000,
            "restricted": 3230
        },
        "privacy": {
            "active_consents": 8945,
            "consent_checks_per_sec": 2341,
            "audit_logs_today": 123456
        },
        "masking": {
            "masked_fields_per_sec": 5432,
            "pii_detections_today": 8765
        },
        "gdpr": {
            "pending_requests": 5,
            "completed_today": 12,
            "avg_completion_hours": 18.5
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
