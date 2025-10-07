from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import sys
import os

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.routes.rules import router as rules_router
from app.routes.templates import router as templates_router
from app.routes.testing import router as testing_router
from app.models.database import init_db

app = FastAPI(
    title="Alert Rules API",
    description="Intelligent alert rule management system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(rules_router, prefix="/api/v1/rules", tags=["rules"])
app.include_router(templates_router, prefix="/api/v1/templates", tags=["templates"])
app.include_router(testing_router, prefix="/api/v1/test", tags=["testing"])

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/")
async def root():
    return {"message": "Alert Rules API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "alert-rules-api"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
