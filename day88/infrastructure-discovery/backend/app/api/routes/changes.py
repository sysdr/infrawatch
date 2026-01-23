from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, text
from datetime import datetime, timedelta
from typing import Optional

from app.utils.database import get_db
from app.models.resource import Change
from app.utils.redis_client import redis_client

router = APIRouter()

@router.get("/recent")
async def get_recent_changes(
    hours: int = Query(24, le=168),
    change_type: Optional[str] = None,
    limit: int = Query(100, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get recent changes"""
    since = datetime.utcnow() - timedelta(hours=hours)
    
    query = select(Change).where(Change.detected_at >= since)
    
    if change_type:
        query = query.where(Change.change_type == change_type)
    
    query = query.order_by(Change.detected_at.desc()).limit(limit)
    result = await db.execute(query)
    changes = result.scalars().all()
    
    return {
        "changes": [
            {
                "id": c.id,
                "resource_id": c.resource_id,
                "type": c.change_type,
                "detected_at": c.detected_at.isoformat(),
                "diff": c.diff
            }
            for c in changes
        ],
        "total": len(changes)
    }

@router.get("/stats")
async def get_change_stats(db: AsyncSession = Depends(get_db)):
    """Get change statistics"""
    # Get stats from Redis
    stats = await redis_client.hgetall("changes:stats")
    
    # Get hourly change rate
    since = datetime.utcnow() - timedelta(hours=1)
    result = await db.execute(
        select(func.count(Change.id))
        .where(Change.detected_at >= since)
    )
    hourly_rate = result.scalar()
    
    # Get changes by type
    result = await db.execute(
        select(Change.change_type, func.count(Change.id))
        .group_by(Change.change_type)
    )
    by_type = dict(result.all())
    
    return {
        "total_changes": sum(int(v) for v in stats.values()) if stats else 0,
        "hourly_rate": hourly_rate,
        "by_type": by_type,
        "stats": stats
    }

@router.get("/timeline")
async def get_change_timeline(
    hours: int = Query(24, le=168),
    db: AsyncSession = Depends(get_db)
):
    """Get change timeline for visualization"""
    since = datetime.utcnow() - timedelta(hours=hours)
    
    # Group changes by hour
    query = text("""
        SELECT 
            DATE_TRUNC('hour', detected_at) as hour,
            change_type,
            COUNT(*) as count
        FROM changes
        WHERE detected_at >= :since
        GROUP BY hour, change_type
        ORDER BY hour
    """)
    
    result = await db.execute(query, {"since": since})
    timeline = result.all()
    
    return {
        "timeline": [
            {
                "timestamp": row[0].isoformat(),
                "type": row[1],
                "count": row[2]
            }
            for row in timeline
        ]
    }
