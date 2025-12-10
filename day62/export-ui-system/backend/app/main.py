from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routes import exports
from app.websocket.manager import sio
import socketio

app = FastAPI(title="Export UI API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
@app.on_event("startup")
def startup_event():
    init_db()

# Include routes
app.include_router(exports.router, prefix="/api", tags=["exports"])

# Mount Socket.IO
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

@app.get("/")
def read_root():
    return {"message": "Export UI API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
