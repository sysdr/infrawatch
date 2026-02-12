from fastapi import APIRouter
from app.api.v1.endpoints import workflows, executions, security, monitoring

api_router = APIRouter()

api_router.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
api_router.include_router(executions.router, prefix="/executions", tags=["executions"])
api_router.include_router(security.router, prefix="/security", tags=["security"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
