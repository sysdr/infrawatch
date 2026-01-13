from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.endpoints import users, teams, permissions, tests, websocket
from app.core.database import engine, Base

app = FastAPI(title="User Management Integration System", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(teams.router, prefix="/api/teams", tags=["teams"])
app.include_router(permissions.router, prefix="/api/permissions", tags=["permissions"])
app.include_router(tests.router, prefix="/api/tests", tags=["tests"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])

@app.get("/")
def read_root():
    return {"message": "User Management Integration API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
