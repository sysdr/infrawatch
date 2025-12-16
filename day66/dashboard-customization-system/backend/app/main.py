from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
from app.database import init_db
from app.routes import dashboard, auth
from app.redis_client import CacheService
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Dashboard Customization API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Socket.IO
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    logger=False,
    engineio_logger=False
)
socket_app = socketio.ASGIApp(sio, app)

# Include routers
app.include_router(dashboard.router)
app.include_router(auth.router)

@app.on_event("startup")
async def startup():
    await init_db()
    print("Database initialized")

@app.get("/api/health")
async def health():
    return {"status": "healthy"}

# WebSocket handlers
@sio.on('connect')
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.on('disconnect')
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

@sio.on('join_dashboard')
async def join_dashboard(sid, data):
    dashboard_id = data.get('dashboard_id')
    user_id = data.get('user_id')
    
    await sio.enter_room(sid, f"dashboard-{dashboard_id}")
    CacheService.set_user_presence(dashboard_id, user_id)
    
    active_users = CacheService.get_active_users(dashboard_id)
    await sio.emit('user_joined', {
        'user_id': user_id,
        'active_users': list(active_users)
    }, room=f"dashboard-{dashboard_id}")

@sio.on('leave_dashboard')
async def leave_dashboard(sid, data):
    dashboard_id = data.get('dashboard_id')
    user_id = data.get('user_id')
    
    await sio.leave_room(sid, f"dashboard-{dashboard_id}")
    CacheService.remove_user_presence(dashboard_id, user_id)
    
    await sio.emit('user_left', {
        'user_id': user_id
    }, room=f"dashboard-{dashboard_id}")

@sio.on('widget_update')
async def widget_update(sid, data):
    dashboard_id = data.get('dashboard_id')
    await sio.emit('widget_updated', data, room=f"dashboard-{dashboard_id}", skip_sid=sid)

@sio.on('theme_change')
async def theme_change(sid, data):
    dashboard_id = data.get('dashboard_id')
    await sio.emit('theme_changed', data, room=f"dashboard-{dashboard_id}", skip_sid=sid)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(socket_app, host="0.0.0.0", port=8000)
