import socketio
from typing import Dict, Set
import asyncio

sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    logger=True,
    engineio_logger=True
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[str]] = {}
    
    async def connect(self, sid: str, job_id: str):
        """Connect a client to a job's progress updates"""
        if job_id not in self.active_connections:
            self.active_connections[job_id] = set()
        self.active_connections[job_id].add(sid)
        print(f"Client {sid} connected to job {job_id}")
    
    async def disconnect(self, sid: str):
        """Disconnect a client"""
        for job_id, connections in self.active_connections.items():
            if sid in connections:
                connections.remove(sid)
                print(f"Client {sid} disconnected from job {job_id}")
                break
    
    async def send_progress(self, job_id: str, data: dict):
        """Send progress update to all clients watching this job"""
        if job_id in self.active_connections:
            for sid in self.active_connections[job_id]:
                try:
                    await sio.emit('progress', data, room=sid)
                except Exception as e:
                    print(f"Error sending progress to {sid}: {e}")

manager = ConnectionManager()

@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")
    await sio.emit('connected', {'status': 'connected'}, room=sid)

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")
    await manager.disconnect(sid)

@sio.event
async def subscribe(sid, data):
    job_id = data.get('job_id')
    if job_id:
        await manager.connect(sid, job_id)
        await sio.emit('subscribed', {'job_id': job_id}, room=sid)

@sio.event
async def unsubscribe(sid, data):
    await manager.disconnect(sid)
