"""API router module"""
from fastapi import APIRouter
from .integration import router as integration_router
from .discovery import router as discovery_router
from .monitoring import router as monitoring_router
from .costs import router as costs_router
from .tests import router as tests_router

router = APIRouter()

router.include_router(integration_router, prefix="/integration", tags=["integration"])
router.include_router(discovery_router, prefix="/discovery", tags=["discovery"])
router.include_router(monitoring_router, prefix="/monitoring", tags=["monitoring"])
router.include_router(costs_router, prefix="/costs", tags=["costs"])
router.include_router(tests_router, prefix="/tests", tags=["tests"])
