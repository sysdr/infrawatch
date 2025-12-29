from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from app.models.team import Team, TeamMember, TeamActivity, Organization, Role, User
from app.schemas.team import TeamCreate, TeamDashboardMetrics
from typing import List, Optional
import redis.asyncio as redis
from app.config import settings
import json
from datetime import datetime, timedelta

class TeamService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.redis_client = None
    
    async def get_redis(self):
        if not self.redis_client:
            self.redis_client = await redis.from_url(settings.REDIS_URL, decode_responses=True)
        return self.redis_client
    
    async def create_team(self, team_data: TeamCreate, creator_id: int) -> Team:
        # Build materialized path
        path = f"/org{team_data.organization_id}"
        if team_data.parent_team_id:
            result = await self.db.execute(
                select(Team).where(Team.id == team_data.parent_team_id)
            )
            parent = result.scalar_one_or_none()
            if parent:
                path = f"{parent.materialized_path}/{parent.slug}"
        
        slug = team_data.name.lower().replace(" ", "-")
        path = f"{path}/{slug}"
        
        team = Team(
            organization_id=team_data.organization_id,
            parent_team_id=team_data.parent_team_id,
            name=team_data.name,
            slug=slug,
            description=team_data.description,
            materialized_path=path,
            team_metadata=team_data.metadata
        )
        
        self.db.add(team)
        await self.db.flush()
        
        # Add creator as admin
        admin_role = await self._get_or_create_role("admin", ["all"])
        member = TeamMember(
            team_id=team.id,
            user_id=creator_id,
            role_id=admin_role.id,
            effective_permissions=["all"]
        )
        self.db.add(member)
        
        team.member_count = 1
        await self.db.commit()
        await self.db.refresh(team)
        
        # Cache team data
        await self._cache_team(team)
        
        return team
    
    async def add_team_member(self, team_id: int, user_id: int, role_id: int, inviter_id: int) -> TeamMember:
        # Compute effective permissions
        role_result = await self.db.execute(select(Role).where(Role.id == role_id))
        role = role_result.scalar_one()
        
        effective_perms = await self._compute_effective_permissions(team_id, role.permissions)
        
        member = TeamMember(
            team_id=team_id,
            user_id=user_id,
            role_id=role_id,
            invited_by=inviter_id,
            effective_permissions=effective_perms
        )
        
        self.db.add(member)
        
        # Update team member count
        result = await self.db.execute(select(Team).where(Team.id == team_id))
        team = result.scalar_one()
        team.member_count += 1
        
        await self.db.commit()
        
        # Invalidate cache
        redis_client = await self.get_redis()
        await redis_client.delete(f"team:{team_id}:members")
        await redis_client.delete(f"perms:user:{user_id}:team:{team_id}")
        await redis_client.delete(f"dashboard:team:{team_id}")  # Invalidate dashboard cache
        
        # Record activity
        await self._record_activity(team_id, inviter_id, "member_added", f"Added user {user_id}")
        
        return member
    
    async def get_team_dashboard(self, team_id: int) -> TeamDashboardMetrics:
        redis_client = await self.get_redis()
        
        # Check cache
        cache_key = f"dashboard:team:{team_id}"
        cached = await redis_client.get(cache_key)
        if cached:
            return TeamDashboardMetrics(**json.loads(cached))
        
        # Compute metrics
        team_result = await self.db.execute(select(Team).where(Team.id == team_id))
        team = team_result.scalar_one()
        
        # Count actual total members from TeamMember table
        total_members_result = await self.db.execute(
            select(func.count(TeamMember.id)).where(TeamMember.team_id == team_id)
        )
        total_members = total_members_result.scalar() or 0
        
        # Update team.member_count to match actual count (sync)
        if team.member_count != total_members:
            team.member_count = total_members
            await self.db.commit()
        
        # Active members today
        today = datetime.utcnow().date()
        active_today_result = await self.db.execute(
            select(func.count(func.distinct(TeamActivity.user_id)))
            .where(
                and_(
                    TeamActivity.team_id == team_id,
                    func.date(TeamActivity.created_at) == today
                )
            )
        )
        active_today = active_today_result.scalar() or 0
        
        # Active members this week
        week_ago = datetime.utcnow() - timedelta(days=7)
        active_week_result = await self.db.execute(
            select(func.count(func.distinct(TeamActivity.user_id)))
            .where(
                and_(
                    TeamActivity.team_id == team_id,
                    TeamActivity.created_at >= week_ago
                )
            )
        )
        active_week = active_week_result.scalar() or 0
        
        # Total activities
        total_activities_result = await self.db.execute(
            select(func.count(TeamActivity.id)).where(TeamActivity.team_id == team_id)
        )
        total_activities = total_activities_result.scalar() or 0
        
        # Recent activities
        recent_result = await self.db.execute(
            select(TeamActivity)
            .where(TeamActivity.team_id == team_id)
            .order_by(desc(TeamActivity.created_at))
            .limit(10)
        )
        recent_activities = [
            {
                "id": act.id,
                "user_id": act.user_id,
                "type": act.activity_type,
                "description": act.description,
                "created_at": act.created_at.isoformat()
            }
            for act in recent_result.scalars().all()
        ]
        
        # Member activity distribution
        dist_result = await self.db.execute(
            select(
                TeamActivity.user_id,
                func.count(TeamActivity.id).label('count')
            )
            .where(TeamActivity.team_id == team_id)
            .group_by(TeamActivity.user_id)
        )
        distribution = {str(row[0]): row[1] for row in dist_result.all()}
        
        metrics = TeamDashboardMetrics(
            team_id=team_id,
            team_name=team.name,
            total_members=total_members,  # Use actual count, not cached member_count
            active_members_today=active_today,
            active_members_week=active_week,
            total_activities=total_activities,
            recent_activities=recent_activities,
            member_activity_distribution=distribution
        )
        
        # Cache for 5 minutes
        await redis_client.setex(
            cache_key,
            300,
            json.dumps(metrics.model_dump(), default=str)
        )
        
        return metrics
    
    async def _compute_effective_permissions(self, team_id: int, base_permissions: List[str]) -> List[str]:
        # Get parent team permissions
        team_result = await self.db.execute(select(Team).where(Team.id == team_id))
        team = team_result.scalar_one()
        
        effective = set(base_permissions)
        
        if team.parent_team_id:
            # Inherit from parent (simplified)
            parent_result = await self.db.execute(
                select(Team).where(Team.id == team.parent_team_id)
            )
            parent = parent_result.scalar_one_or_none()
            if parent:
                # In production, traverse full hierarchy
                effective.update(["read"])  # Inherit basic read permission
        
        return list(effective)
    
    async def _get_or_create_role(self, name: str, permissions: List[str]) -> Role:
        result = await self.db.execute(select(Role).where(Role.name == name))
        role = result.scalar_one_or_none()
        
        if not role:
            role = Role(name=name, permissions=permissions, is_system_role=True)
            self.db.add(role)
            await self.db.flush()
        
        return role
    
    async def _cache_team(self, team: Team):
        redis_client = await self.get_redis()
        team_data = {
            "id": team.id,
            "name": team.name,
            "slug": team.slug,
            "path": team.materialized_path
        }
        await redis_client.setex(f"team:{team.id}", 900, json.dumps(team_data))
    
    async def _record_activity(self, team_id: int, user_id: int, activity_type: str, description: str):
        activity = TeamActivity(
            team_id=team_id,
            user_id=user_id,
            activity_type=activity_type,
            description=description
        )
        self.db.add(activity)
        await self.db.commit()
        
        # Publish to Redis for real-time updates
        redis_client = await self.get_redis()
        await redis_client.publish(
            f"team:{team_id}:events",
            json.dumps({
                "type": activity_type,
                "user_id": user_id,
                "description": description,
                "timestamp": datetime.utcnow().isoformat()
            })
        )
