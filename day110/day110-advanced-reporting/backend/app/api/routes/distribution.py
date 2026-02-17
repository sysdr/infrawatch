from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db, DistributionList, ReportExecution, ReportState
from app.api.schemas.report_schemas import DistributionListCreate
from app.services.distributors.email_distributor import EmailDistributor
from typing import List

router = APIRouter()

@router.post("/lists")
def create_distribution_list(dist_list: DistributionListCreate, db: Session = Depends(get_db)):
    """Create a new distribution list"""
    
    existing = db.query(DistributionList).filter(DistributionList.name == dist_list.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Distribution list name already exists")
    
    db_list = DistributionList(
        name=dist_list.name,
        recipients=dist_list.recipients,
        channels=dist_list.channels
    )
    
    db.add(db_list)
    db.commit()
    db.refresh(db_list)
    
    return db_list

@router.get("/lists")
def list_distribution_lists(db: Session = Depends(get_db)):
    """List all distribution lists"""
    lists = db.query(DistributionList).all()
    return lists

@router.post("/send/{execution_id}/{list_id}")
async def distribute_report(execution_id: int, list_id: int, db: Session = Depends(get_db)):
    """Distribute a completed report to distribution list"""
    
    execution = db.query(ReportExecution).filter(ReportExecution.id == execution_id).first()
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    if execution.state != ReportState.COMPLETED:
        raise HTTPException(status_code=400, detail="Report generation not completed")
    
    dist_list = db.query(DistributionList).filter(DistributionList.id == list_id).first()
    if not dist_list:
        raise HTTPException(status_code=404, detail="Distribution list not found")
    
    # Send to recipients
    distributor = EmailDistributor()
    email_recipients = [r["address"] for r in dist_list.recipients if r["type"] == "email"]
    
    results = await distributor.send_report(
        email_recipients,
        execution.output_paths,
        f"Report: {execution.report_id}"
    )
    
    # Update execution with distribution results
    execution.distributed_to = results
    db.commit()
    
    return {"status": "distributed", "results": results}
