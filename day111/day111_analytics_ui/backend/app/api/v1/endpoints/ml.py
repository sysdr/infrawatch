from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.ml_service import MLService
from app.schemas.analytics import MLPredictRequest, MLPredictResponse

router = APIRouter(prefix="/ml", tags=["ml"])

@router.post("/predict", response_model=MLPredictResponse)
async def predict(payload: MLPredictRequest, db: AsyncSession = Depends(get_db)):
    svc = MLService(db)
    return await svc.predict(payload.features, payload.model_name)

@router.get("/models")
async def list_models(db: AsyncSession = Depends(get_db)):
    from app.models.analytics import MLModel
    from sqlalchemy import select
    result = await db.execute(select(MLModel).order_by(MLModel.trained_at.desc()))
    models = result.scalars().all()
    return [{"id": m.id, "name": m.name, "version": m.version,
             "metrics": m.metrics, "is_active": m.is_active,
             "trained_at": m.trained_at.isoformat()} for m in models]
