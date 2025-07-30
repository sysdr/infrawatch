from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import servers_router
from app.core.database import engine
from app.models import server, audit

# Create database tables
server.Base.metadata.create_all(bind=engine)
audit.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Server Management API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(servers_router)

@app.get("/")
def read_root():
    return {"message": "Server Management API", "version": "1.0.0"}
