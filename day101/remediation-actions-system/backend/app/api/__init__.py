from fastapi import APIRouter
from .remediation import router as remediation_router

api_router = APIRouter()
api_router.include_router(remediation_router, prefix="/remediation", tags=["remediation"])
