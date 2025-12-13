from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import charts

app = FastAPI(title="Advanced Charts API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(charts.router, prefix="/api/charts", tags=["charts"])

@app.get("/")
async def root():
    return {
        "message": "Advanced Charts API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
