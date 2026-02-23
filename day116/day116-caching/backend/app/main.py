import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.cache.redis_cache import CacheManager
from app.api.cache_routes import router as cache_router
from app.api.metrics_routes import router as metrics_router

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

@asynccontextmanager
async def lifespan(app: FastAPI):
    cache = CacheManager(redis_url=REDIS_URL)
    await cache.connect()
    app.state.cache = cache
    yield
    await cache.disconnect()

app = FastAPI(title="Day 116 — Caching", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(cache_router)
app.include_router(metrics_router)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "cache-system"}
