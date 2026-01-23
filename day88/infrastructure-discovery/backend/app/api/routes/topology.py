from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from typing import Optional

from app.utils.database import get_db
from app.models.resource import Resource, Relationship

router = APIRouter()

@router.get("/graph")
async def get_topology_graph(
    resource_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get topology graph"""
    # Get all resources
    result = await db.execute(select(Resource))
    resources = result.scalars().all()
    
    # Get all relationships
    result = await db.execute(select(Relationship))
    relationships = result.scalars().all()
    
    nodes = [
        {
            "id": r.id,
            "name": r.name,
            "type": r.resource_type,
            "group": r.resource_type,
            "state": r.state
        }
        for r in resources
    ]
    
    links = [
        {
            "source": rel.source_id,
            "target": rel.target_id,
            "type": rel.relationship_type
        }
        for rel in relationships
    ]
    
    return {
        "nodes": nodes,
        "links": links
    }

@router.get("/dependencies/{resource_id}")
async def get_dependencies(
    resource_id: str,
    depth: int = Query(5, le=10),
    db: AsyncSession = Depends(get_db)
):
    """Get resource dependencies using recursive query"""
    query = text("""
        WITH RECURSIVE deps AS (
            SELECT target_id, relationship_type, 1 as depth
            FROM relationships
            WHERE source_id = :resource_id
            
            UNION
            
            SELECT r.target_id, r.relationship_type, deps.depth + 1
            FROM relationships r
            JOIN deps ON r.source_id = deps.target_id
            WHERE deps.depth < :max_depth
        )
        SELECT DISTINCT target_id, relationship_type, depth
        FROM deps
        ORDER BY depth, target_id
    """)
    
    result = await db.execute(
        query,
        {"resource_id": resource_id, "max_depth": depth}
    )
    dependencies = result.all()
    
    # Get resource details for dependencies
    dep_ids = [d[0] for d in dependencies]
    if dep_ids:
        result = await db.execute(
            select(Resource).where(Resource.id.in_(dep_ids))
        )
        dep_resources = {r.id: r for r in result.scalars().all()}
    else:
        dep_resources = {}
    
    return {
        "resource_id": resource_id,
        "dependencies": [
            {
                "id": d[0],
                "relationship": d[1],
                "depth": d[2],
                "name": dep_resources[d[0]].name if d[0] in dep_resources else "Unknown",
                "type": dep_resources[d[0]].resource_type if d[0] in dep_resources else "Unknown"
            }
            for d in dependencies
        ],
        "total": len(dependencies)
    }

@router.get("/dependents/{resource_id}")
async def get_dependents(
    resource_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get resources that depend on this resource"""
    result = await db.execute(
        select(Relationship).where(Relationship.target_id == resource_id)
    )
    relationships = result.scalars().all()
    
    # Get resource details
    source_ids = [rel.source_id for rel in relationships]
    if source_ids:
        result = await db.execute(
            select(Resource).where(Resource.id.in_(source_ids))
        )
        resources = {r.id: r for r in result.scalars().all()}
    else:
        resources = {}
    
    return {
        "resource_id": resource_id,
        "dependents": [
            {
                "id": rel.source_id,
                "relationship": rel.relationship_type,
                "name": resources[rel.source_id].name if rel.source_id in resources else "Unknown",
                "type": resources[rel.source_id].resource_type if rel.source_id in resources else "Unknown"
            }
            for rel in relationships
        ],
        "total": len(relationships)
    }
