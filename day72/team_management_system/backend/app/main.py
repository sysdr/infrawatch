from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.api import teams
from app.database import engine, Base
from app.websocket.team_ws import manager
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()

app = FastAPI(title="Team Management System", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=False,  # Must be False when using allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(teams.router)

@app.get("/")
async def root():
    return {
        "message": "Team Management System API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "api": "/api/teams"
    }

@app.websocket("/ws/teams/{team_id}")
async def team_websocket(websocket: WebSocket, team_id: int, user_id: int = 1):
    await manager.connect(websocket, team_id, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo messages for demo
            await manager.broadcast_to_team(team_id, {
                "type": "message",
                "user_id": user_id,
                "content": data
            })
    except WebSocketDisconnect:
        manager.disconnect(team_id, user_id)

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/favicon.ico")
async def favicon():
    from fastapi.responses import Response
    return Response(status_code=204)
