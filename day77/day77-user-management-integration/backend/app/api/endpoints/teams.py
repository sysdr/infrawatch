from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.services.team_service import TeamService
from app.schemas.team import TeamCreate, TeamResponse, TeamMemberAdd, TeamMemberResponse

router = APIRouter()

@router.post("/", response_model=TeamResponse)
def create_team(team: TeamCreate, db: Session = Depends(get_db)):
    return TeamService.create_team(db, team)

@router.get("/{team_id}", response_model=TeamResponse)
def get_team(team_id: int, db: Session = Depends(get_db)):
    team = TeamService.get_team(db, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team

@router.get("/", response_model=List[TeamResponse])
def get_teams(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return TeamService.get_teams(db, skip, limit)

@router.post("/{team_id}/members", response_model=TeamMemberResponse)
def add_team_member(team_id: int, member: TeamMemberAdd, db: Session = Depends(get_db)):
    return TeamService.add_member(db, team_id, member)

@router.delete("/{team_id}/members/{user_id}")
def remove_team_member(team_id: int, user_id: int, db: Session = Depends(get_db)):
    success = TeamService.remove_member(db, team_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Member not found")
    return {"message": "Member removed successfully"}
