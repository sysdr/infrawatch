from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.services.workflow_service import ScriptService

router = APIRouter()

class ScriptCreate(BaseModel):
    name: str
    description: str
    script_type: str
    content: str
    workflow_id: int = None

class ScriptUpdate(BaseModel):
    name: str = None
    description: str = None
    content: str = None
    is_active: bool = None

@router.post("/scripts")
def create_script(script: ScriptCreate, db: Session = Depends(get_db)):
    return ScriptService.create_script(db, script.name, script.description, script.script_type, script.content, script.workflow_id)

@router.get("/scripts")
def list_scripts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    scripts = ScriptService.get_scripts(db, skip, limit)
    return {"scripts": scripts, "total": len(scripts)}

@router.get("/scripts/{script_id}")
def get_script(script_id: int, db: Session = Depends(get_db)):
    script = ScriptService.get_script(db, script_id)
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    return script

@router.put("/scripts/{script_id}")
def update_script(script_id: int, updates: ScriptUpdate, db: Session = Depends(get_db)):
    update_dict = {k: v for k, v in updates.model_dump().items() if v is not None}
    script = ScriptService.update_script(db, script_id, update_dict)
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    return script

@router.delete("/scripts/{script_id}")
def delete_script(script_id: int, db: Session = Depends(get_db)):
    success = ScriptService.delete_script(db, script_id)
    if not success:
        raise HTTPException(status_code=404, detail="Script not found")
    return {"message": "Script deleted successfully"}
