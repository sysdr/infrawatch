from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.database import engine, Base, get_db
from app.core.redis_client import close_redis, get_redis
from app.api.v1.router import api_router
from app.services.analytics_service import AnalyticsService
from app.services.ml_service import MLService
from app.services.config_service import ConfigService

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables, seed data, train model
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    from app.core.database import AsyncSessionFactory
    async with AsyncSessionFactory() as db:
        redis = await get_redis()
        await AnalyticsService(db, redis).seed_metrics()
        await MLService(db).ensure_model_exists()
        await ConfigService(db).seed_defaults()

    yield
    await close_redis()

app = FastAPI(title="Analytics UI API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "analytics-ui", "version": "1.0.0"}


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_html(db: AsyncSession = Depends(get_db), redis=Depends(get_redis)):
    """Simple HTML dashboard (backend-rendered) for verification."""
    svc = AnalyticsService(db, redis)
    data = await svc.get_dashboard()
    kpis = data.kpis
    updated = data.updated_at.isoformat() if data.updated_at else ""
    rows = "".join(
        f"""
        <tr>
            <td>{k.name.replace('_', ' ')}</td>
            <td>{k.value:.1f} {k.unit}</td>
            <td>{k.trend_direction}</td>
            <td>{k.trend:+.1f}%</td>
        </tr>"""
        for k in kpis
    )
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Analytics Dashboard</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ font-family: system-ui, sans-serif; background: #0f1923; color: #e8f5e9; margin: 0; padding: 2rem; }}
    h1 {{ color: #52b788; margin-bottom: 0.5rem; }}
    .sub {{ color: #8899aa; font-size: 0.9rem; margin-bottom: 1.5rem; }}
    table {{ border-collapse: collapse; width: 100%; max-width: 640px; background: #1a2535; border: 1px solid #2a3f55; border-radius: 8px; overflow: hidden; }}
    th, td {{ padding: 12px 16px; text-align: left; border-bottom: 1px solid #2a3f55; }}
    th {{ background: #162030; color: #52b788; font-weight: 600; }}
    tr:hover {{ background: #162030; }}
    .ok {{ color: #52b788; }}
    .up {{ color: #52b788; }}
    .down {{ color: #74c69d; }}
  </style>
</head>
<body>
  <h1>Infrastructure Dashboard</h1>
  <p class="sub">Last updated: {updated}</p>
  <table>
    <thead><tr><th>Metric</th><th>Value</th><th>Trend</th><th>Change</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
  <p class="sub" style="margin-top: 1.5rem;"><a href="/docs" style="color: #52b788;">API Docs</a> &middot; <a href="/health" style="color: #52b788;">Health</a></p>
</body>
</html>"""
    return html
