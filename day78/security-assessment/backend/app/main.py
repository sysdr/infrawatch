from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.utils.database import init_db
import os

app = FastAPI(title="Security Assessment Platform", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
@app.on_event("startup")
async def startup_event():
    init_db()
    # Create scan target directory
    os.makedirs("/tmp/scan_target", exist_ok=True)

app.include_router(router, prefix="/api/security", tags=["security"])

@app.get("/")
async def root():
    return {"message": "Security Assessment Platform API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
