from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routes import router
import os

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Dashboard Templates API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1", tags=["templates"])

@app.get("/")
def root():
    return {"message": "Dashboard Templates API", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}
