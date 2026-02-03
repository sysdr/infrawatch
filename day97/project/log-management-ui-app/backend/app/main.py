"""Log Management UI - FastAPI backend."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.logs import router as logs_router

app = FastAPI(title="Log Management API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(logs_router, prefix="/api", tags=["logs"])


@app.get("/health")
def health():
    return {"status": "ok"}
