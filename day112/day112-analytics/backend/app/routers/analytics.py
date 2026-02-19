from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.pipeline import get_pipeline_status, ingest_event, get_event_summary

router = APIRouter()

@router.get("/pipeline")
def pipeline_status():
    return get_pipeline_status()

@router.post("/events")
def post_event(body: dict, db: Session = Depends(get_db)):
    return ingest_event(db, body)

@router.get("/summary")
def event_summary(db: Session = Depends(get_db)):
    return get_event_summary(db)
