from fastapi import APIRouter
from app.api.v1.endpoints import analytics, ml, reports, config

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(analytics.router)
api_router.include_router(ml.router)
api_router.include_router(reports.router)
api_router.include_router(config.router)
