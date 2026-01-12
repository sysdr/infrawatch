from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from .models import Base
from .api.routes import router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="User Directory Features API",
    description="Enterprise identity integration with LDAP, SSO, and lifecycle management",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1", tags=["users"])

@app.get("/")
def root():
    return {
        "message": "User Directory Features API",
        "version": "1.0.0",
        "features": [
            "LDAP/AD Integration",
            "SSO/SAML Support",
            "User Import/Export",
            "Automated Provisioning",
            "Lifecycle Management"
        ]
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "user-directory"}
