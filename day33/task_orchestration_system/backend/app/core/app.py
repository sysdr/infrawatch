from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import json
import asyncio
from typing import Dict, List
from ..orchestration.workflow_engine import WorkflowEngine
from ..orchestration.task_manager import TaskManager
from ..api.routes import router

def create_app() -> FastAPI:
    app = FastAPI(title="Task Orchestration System", version="1.0.0")
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize task system
    task_manager = TaskManager()
    workflow_engine = WorkflowEngine(task_manager)
    
    # Store in app state
    app.state.task_manager = task_manager
    app.state.workflow_engine = workflow_engine
    
    # Include routes
    app.include_router(router, prefix="/api/v1")
    
    # WebSocket connections manager
    class ConnectionManager:
        def __init__(self):
            self.active_connections: List[WebSocket] = []

        async def connect(self, websocket: WebSocket):
            await websocket.accept()
            self.active_connections.append(websocket)

        def disconnect(self, websocket: WebSocket):
            self.active_connections.remove(websocket)

        async def broadcast(self, message: str):
            for connection in self.active_connections:
                try:
                    await connection.send_text(message)
                except:
                    pass

    manager = ConnectionManager()
    app.state.websocket_manager = manager

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await manager.connect(websocket)
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            manager.disconnect(websocket)

    return app
