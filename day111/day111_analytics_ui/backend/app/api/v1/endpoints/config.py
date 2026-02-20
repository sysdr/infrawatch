from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.config_service import ConfigService
from app.schemas.analytics import ConfigUpdate

router = APIRouter(prefix="/config", tags=["config"])

@router.get("/")
async def get_config(db: AsyncSession = Depends(get_db)):
    return await ConfigService(db).get_all()

@router.patch("/")
async def update_config(payload: ConfigUpdate, db: AsyncSession = Depends(get_db)):
    return await ConfigService(db).update(payload)
