from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.test_service import TestService
from typing import Dict

router = APIRouter()

@router.post("/run-integration-tests")
def run_integration_tests(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    test_id = TestService.start_test_suite(db)
    background_tasks.add_task(TestService.run_all_tests, db, test_id)
    return {"test_id": test_id, "status": "started"}

@router.get("/results/{test_id}")
def get_test_results(test_id: str, db: Session = Depends(get_db)):
    return TestService.get_test_results(db, test_id)

@router.get("/status")
def get_test_status(db: Session = Depends(get_db)):
    return TestService.get_current_status(db)
