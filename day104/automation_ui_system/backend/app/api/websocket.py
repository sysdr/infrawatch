import asyncio
import json
import socketio
from redis.asyncio import Redis

from app.core.config import settings

sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*'
)

# socketio_path='/' because we mount at /socket.io - the mount strips the prefix so engineio receives path /
socket_app = socketio.ASGIApp(sio, socketio_path='/')


async def _redis_listener():
    """Subscribe to Redis workflow_updates and emit to Socket.IO clients."""
    redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB, decode_responses=True)
    pubsub = redis.pubsub()
    await pubsub.subscribe('workflow_updates')
    try:
        async for message in pubsub.listen():
            if message and message.get('type') == 'message' and message.get('data'):
                try:
                    data = json.loads(message['data']) if isinstance(message['data'], str) else message['data']
                    await sio.emit('workflow_update', data)
                except (json.JSONDecodeError, TypeError):
                    await sio.emit('workflow_update', {'type': 'update'})
    except asyncio.CancelledError:
        pass
    finally:
        await pubsub.unsubscribe('workflow_updates')
        await pubsub.close()
        await redis.close()


def start_redis_listener():
    """Start the Redis listener as a background task. Call from FastAPI startup."""
    asyncio.create_task(_redis_listener())


@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")
    await sio.emit('connected', {'message': 'Connected to workflow updates'}, room=sid)


@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")
