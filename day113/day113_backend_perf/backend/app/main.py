import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from app.core.config import get_settings
from app.core.middleware import MetricsMiddleware
from app.api import users, metrics
from app.db.session import engine, Base
settings = get_settings()
logging.basicConfig(level=logging.INFO)
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
app = FastAPI(title=settings.APP_NAME, description="Day 113: Backend Performance Demo", version="1.0.0", lifespan=lifespan)
app.add_middleware(MetricsMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1024)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(users.router, prefix=settings.API_PREFIX)
app.include_router(metrics.router, prefix=settings.API_PREFIX)
metrics_app = make_asgi_app()
app.mount("/metrics/prometheus", metrics_app)
@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.APP_NAME}
