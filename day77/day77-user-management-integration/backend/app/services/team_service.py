from sqlalchemy.orm import Session
from app.models import Team, TeamMember, TeamRole, AuditLog
from app.schemas.team import TeamCreate, TeamMemberAdd
from datetime import datetime
from app.core.redis_client import get_redis
from typing import List

class TeamService:
    @staticmethod
    def create_team(db: Session, team_data: TeamCreate) -> Team:
        team = Team(**team_data.dict())
        db.add(team)
        db.flush()
        
        # Log audit
        audit = AuditLog(
            action="team_created",
            resource_type="team",
            resource_id=str(team.id),
            details={"name": team.name}
        )
        db.add(audit)
        db.commit()
        db.refresh(team)
        
        return team
    
    @staticmethod
    def get_team(db: Session, team_id: int) -> Team:
        return db.query(Team).filter(Team.id == team_id).first()
    
    @staticmethod
    def get_teams(db: Session, skip: int = 0, limit: int = 100):
        return db.query(Team).offset(skip).limit(limit).all()
    
    @staticmethod
    def add_member(db: Session, team_id: int, member_data: TeamMemberAdd) -> TeamMember:
        member = TeamMember(
            team_id=team_id,
            user_id=member_data.user_id,
            role=member_data.role
        )
        db.add(member)
        db.flush()
        
        # Log audit
        audit = AuditLog(
            user_id=member_data.user_id,
            action="team_member_added",
            resource_type="team",
            resource_id=str(team_id),
            details={"role": member_data.role.value}
        )
        db.add(audit)
        db.commit()
        db.refresh(member)
        
        # Invalidate permission cache
        redis = get_redis()
        redis.delete(f"permissions:user:{member_data.user_id}")
        
        return member
    
    @staticmethod
    def remove_member(db: Session, team_id: int, user_id: int) -> bool:
        member = db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id
        ).first()
        
        if not member:
            return False
        
        # Log audit before deletion
        audit = AuditLog(
            user_id=user_id,
            action="team_member_removed",
            resource_type="team",
            resource_id=str(team_id)
        )
        db.add(audit)
        
        db.delete(member)
        db.commit()
        
        # Invalidate permission cache
        redis = get_redis()
        redis.delete(f"permissions:user:{user_id}")
        
        return True
    
    @staticmethod
    def get_team_hierarchy(db: Session, team_id: int) -> List[Team]:
        """Get all parent teams in hierarchy"""
        hierarchy = []
        current_team = db.query(Team).filter(Team.id == team_id).first()
        
        while current_team:
            hierarchy.append(current_team)
            if current_team.parent_id:
                current_team = db.query(Team).filter(Team.id == current_team.parent_id).first()
            else:
                break
        
        return hierarchy
