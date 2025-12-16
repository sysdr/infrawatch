from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from app.models import Dashboard, DashboardVersion, DashboardShare
from app.schemas import DashboardCreate, DashboardUpdate
from app.redis_client import CacheService
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timedelta
import uuid

class DashboardService:
    @staticmethod
    async def create_dashboard(db: AsyncSession, dashboard: DashboardCreate, owner_id: UUID) -> Dashboard:
        db_dashboard = Dashboard(
            owner_id=owner_id,
            name=dashboard.name,
            description=dashboard.description,
            config=dashboard.config.model_dump(),
            theme=dashboard.theme,
            is_template=dashboard.is_template,
            version=1
        )
        db.add(db_dashboard)
        await db.commit()
        await db.refresh(db_dashboard)
        
        # Save initial version
        version = DashboardVersion(
            dashboard_id=db_dashboard.id,
            version=1,
            config=db_dashboard.config,
            theme=db_dashboard.theme,
            changed_by=owner_id
        )
        db.add(version)
        await db.commit()
        
        return db_dashboard
    
    @staticmethod
    async def get_dashboard(db: AsyncSession, dashboard_id: UUID, user_id: Optional[UUID] = None) -> Optional[Dashboard]:
        # Build query with optional ownership check
        query = select(Dashboard).filter(Dashboard.id == dashboard_id)
        if user_id:
            query = query.filter(Dashboard.owner_id == user_id)
        
        result = await db.execute(query)
        dashboard = result.scalar_one_or_none()
        
        if dashboard:
            cached = CacheService.get_dashboard(str(dashboard_id), dashboard.version)
            if cached:
                return dashboard
            
            # Cache miss - store in cache
            CacheService.set_dashboard(str(dashboard_id), dashboard.version, {
                "config": dashboard.config,
                "theme": dashboard.theme,
                "version": dashboard.version
            })
        
        return dashboard
    
    @staticmethod
    async def update_dashboard(db: AsyncSession, dashboard_id: UUID, update: DashboardUpdate, user_id: UUID) -> Dashboard:
        result = await db.execute(select(Dashboard).filter(Dashboard.id == dashboard_id))
        dashboard = result.scalar_one_or_none()
        
        if not dashboard:
            return None
        
        # Check version for optimistic locking
        if update.version != dashboard.version:
            raise ValueError("Version conflict - dashboard was modified by another user")
        
        # Update fields
        if update.name:
            dashboard.name = update.name
        if update.description is not None:
            dashboard.description = update.description
        if update.config:
            dashboard.config = update.config.model_dump()
        if update.theme:
            dashboard.theme = update.theme
        
        dashboard.version += 1
        dashboard.updated_at = datetime.utcnow()
        
        # Save version history
        version = DashboardVersion(
            dashboard_id=dashboard.id,
            version=dashboard.version,
            config=dashboard.config,
            theme=dashboard.theme,
            changed_by=user_id
        )
        db.add(version)
        
        await db.commit()
        await db.refresh(dashboard)
        
        # Invalidate cache
        CacheService.invalidate_dashboard(str(dashboard_id))
        
        return dashboard
    
    @staticmethod
    async def list_dashboards(db: AsyncSession, owner_id: UUID, is_template: bool = False) -> List[Dashboard]:
        query = select(Dashboard).filter(
            and_(
                Dashboard.owner_id == owner_id,
                Dashboard.is_template == is_template
            )
        ).order_by(Dashboard.updated_at.desc())
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def list_templates(db: AsyncSession) -> List[Dashboard]:
        query = select(Dashboard).filter(Dashboard.is_template == True).order_by(Dashboard.name)
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def create_share(db: AsyncSession, dashboard_id: UUID, permission: str, 
                          expires_in_hours: Optional[int], created_by: UUID) -> DashboardShare:
        share_token = str(uuid.uuid4())
        expires_at = None
        if expires_in_hours:
            expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
        
        share = DashboardShare(
            dashboard_id=dashboard_id,
            share_token=share_token,
            permission=permission,
            expires_at=expires_at,
            created_by=created_by
        )
        db.add(share)
        await db.commit()
        await db.refresh(share)
        return share
    
    @staticmethod
    async def get_share(db: AsyncSession, share_token: str) -> Optional[DashboardShare]:
        query = select(DashboardShare).filter(
            and_(
                DashboardShare.share_token == share_token,
                or_(
                    DashboardShare.expires_at.is_(None),
                    DashboardShare.expires_at > datetime.utcnow()
                )
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def list_shares(db: AsyncSession, dashboard_id: UUID) -> List[DashboardShare]:
        query = select(DashboardShare).filter(
            DashboardShare.dashboard_id == dashboard_id
        ).order_by(DashboardShare.created_at.desc())
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def revoke_share(db: AsyncSession, share_id: UUID) -> bool:
        result = await db.execute(select(DashboardShare).filter(DashboardShare.id == share_id))
        share = result.scalar_one_or_none()
        if share:
            await db.delete(share)
            await db.commit()
            return True
        return False
