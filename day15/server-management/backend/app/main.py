from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.database import engine, Base
from app.api.servers import router as servers_router

app = FastAPI(
    title="Server Management API",
    description="Distributed Systems Server Management API",
    version="1.0.0"
)

# Create database tables only when app starts
@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(servers_router)

@app.get("/")
def read_root():
    return {"message": "Server Management API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "server-management-api"}
