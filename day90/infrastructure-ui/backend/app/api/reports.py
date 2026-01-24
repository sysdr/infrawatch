from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from sqlalchemy import select, func
from app.models.resource import Resource, Metric
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/reports", tags=["reports"])

@router.get("/inventory")
async def resource_inventory(db: AsyncSession = Depends(get_db)):
    """Complete resource inventory report"""
    query = select(
        Resource.resource_type,
        Resource.cloud_provider,
        Resource.status,
        func.count(Resource.id).label('count')
    ).group_by(
        Resource.resource_type,
        Resource.cloud_provider,
        Resource.status
    )
    
    result = await db.execute(query)
    inventory = [
        {
            'type': row[0],
            'provider': row[1],
            'status': row[2],
            'count': row[3]
        }
        for row in result
    ]
    
    return {
        'report_type': 'inventory',
        'generated_at': datetime.utcnow().isoformat(),
        'data': inventory
    }

@router.get("/utilization")
async def utilization_report(db: AsyncSession = Depends(get_db)):
    """Resource utilization report"""
    # Get average metrics per resource type
    query = select(
        Resource.resource_type,
        func.avg(Metric.cpu_usage).label('avg_cpu'),
        func.avg(Metric.memory_usage).label('avg_memory')
    ).join(
        Metric, Resource.id == Metric.resource_id
    ).where(
        Metric.timestamp >= datetime.utcnow() - timedelta(hours=24)
    ).group_by(Resource.resource_type)
    
    result = await db.execute(query)
    utilization = [
        {
            'resource_type': row[0],
            'avg_cpu': round(float(row[1] or 0), 2),
            'avg_memory': round(float(row[2] or 0), 2)
        }
        for row in result
    ]
    
    return {
        'report_type': 'utilization',
        'period': 'last_24_hours',
        'generated_at': datetime.utcnow().isoformat(),
        'data': utilization
    }

@router.get("/compliance")
async def compliance_report(db: AsyncSession = Depends(get_db)):
    """Compliance report showing policy violations"""
    # Find resources without required tags
    query = select(Resource).where(
        ~Resource.tags.has_key('environment') |
        ~Resource.tags.has_key('owner') |
        ~Resource.tags.has_key('cost_center')
    )
    
    result = await db.execute(query)
    untagged = result.scalars().all()
    
    violations = []
    for resource in untagged:
        missing_tags = []
        if 'environment' not in resource.tags:
            missing_tags.append('environment')
        if 'owner' not in resource.tags:
            missing_tags.append('owner')
        if 'cost_center' not in resource.tags:
            missing_tags.append('cost_center')
        
        violations.append({
            'resource_id': resource.id,
            'name': resource.name,
            'type': resource.resource_type,
            'violation': 'missing_required_tags',
            'missing_tags': missing_tags
        })
    
    return {
        'report_type': 'compliance',
        'generated_at': datetime.utcnow().isoformat(),
        'total_violations': len(violations),
        'violations': violations
    }
