from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.api import workflows, scripts, analytics
from app.api.websocket import socket_app, start_redis_listener

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(workflows.router, prefix=f"{settings.API_V1_STR}", tags=["workflows"])
app.include_router(scripts.router, prefix=f"{settings.API_V1_STR}", tags=["scripts"])
app.include_router(analytics.router, prefix=f"{settings.API_V1_STR}", tags=["analytics"])

# Mount Socket.IO at /socket.io - use socketio_path='/' since mount strips the prefix
app.mount("/socket.io", socket_app)

@app.on_event("startup")
def startup_event():
    init_db()
    start_redis_listener()

@app.get("/")
def read_root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
