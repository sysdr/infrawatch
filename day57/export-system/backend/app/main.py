from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import exports
from app.models.database import engine, Base

app = FastAPI(title="Export System API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(exports.router, prefix="/api/exports", tags=["exports"])

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "export-system"}

@app.get("/")
async def root():
    return {"message": "Export System API - Day 57"}
