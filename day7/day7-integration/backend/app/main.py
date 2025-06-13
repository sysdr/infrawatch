from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import asyncio
import time
import psutil
from typing import Dict, Any
import os
from datetime import datetime

app = FastAPI(
    title="Day 7 Integration API",
    description="End-to-End Integration Demo",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for demo
app_state = {
    "startup_time": datetime.now(),
    "request_count": 0,
    "hello_count": 0
}

@app.middleware("http")
async def count_requests(request, call_next):
    app_state["request_count"] += 1
    response = await call_next(request)
    return response

@app.get("/")
async def root():
    return {"message": "Day 7 Integration API is running!"}

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    try:
        # System metrics
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Uptime calculation
        uptime = datetime.now() - app_state["startup_time"]
        
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": int(uptime.total_seconds()),
            "system": {
                "memory_used_percent": memory.percent,
                "memory_available_mb": memory.available // (1024 * 1024),
                "cpu_percent": cpu_percent
            },
            "application": {
                "request_count": app_state["request_count"],
                "hello_count": app_state["hello_count"]
            },
            "dependencies": await check_dependencies()
        }
        
        return health_data
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

async def check_dependencies():
    """Check external dependencies"""
    deps = {}
    
    # Simulate database check
    try:
        await asyncio.sleep(0.1)  # Simulate DB query
        deps["database"] = {"status": "connected", "response_time_ms": 100}
    except Exception:
        deps["database"] = {"status": "error", "error": "Connection failed"}
    
    # Simulate Redis check
    try:
        await asyncio.sleep(0.05)  # Simulate Redis ping
        deps["redis"] = {"status": "connected", "response_time_ms": 50}
    except Exception:
        deps["redis"] = {"status": "error", "error": "Connection failed"}
    
    return deps

@app.get("/api/hello")
async def hello_world():
    """Hello World endpoint for frontend integration"""
    app_state["hello_count"] += 1
    
    return {
        "message": "Hello from the backend!",
        "timestamp": datetime.now().isoformat(),
        "count": app_state["hello_count"],
        "server_info": {
            "uptime_seconds": int((datetime.now() - app_state["startup_time"]).total_seconds()),
            "total_requests": app_state["request_count"]
        }
    }

@app.post("/api/echo")
async def echo_message(data: dict):
    """Echo endpoint for testing POST requests"""
    return {
        "echo": data,
        "processed_at": datetime.now().isoformat(),
        "message": "Data received and echoed back"
    }

@app.get("/api/status")
async def get_status():
    """Detailed application status"""
    return {
        "application": "Day 7 Integration Demo",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "startup_time": app_state["startup_time"].isoformat(),
        "metrics": {
            "total_requests": app_state["request_count"],
            "hello_requests": app_state["hello_count"]
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
