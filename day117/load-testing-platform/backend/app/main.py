from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.models.database import init_db
from app.services.metrics import metrics_sampler
from app.routers import target_api, tests, system_metrics
import os, pathlib

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure data dir exists
    pathlib.Path("data").mkdir(exist_ok=True)
    await init_db()
    await metrics_sampler.start()
    yield
    await metrics_sampler.stop()

app = FastAPI(
    title="Load Testing Platform",
    description="Day 117 — Performance Testing Suite for Infrastructure Management",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(target_api.router)
app.include_router(tests.router)
app.include_router(system_metrics.router)

@app.get("/")
async def root():
    return {"service": "Load Testing Platform", "day": 117, "docs": "/docs"}
