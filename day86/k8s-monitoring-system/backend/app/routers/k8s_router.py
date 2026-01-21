from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.core.database import get_db
from models.k8s_models import Pod, Service, Deployment, Node
from typing import List, Optional

router = APIRouter()

@router.get("/pods")
async def get_pods(
    namespace: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all pods with optional filtering"""
    query = select(Pod)
    
    if namespace:
        query = query.where(Pod.namespace == namespace)
    if status:
        query = query.where(Pod.status == status)
    
    query = query.order_by(desc(Pod.updated_at))
    result = await db.execute(query)
    pods = result.scalars().all()
    
    return [
        {
            "name": p.name,
            "namespace": p.namespace,
            "status": p.status,
            "node_name": p.node_name,
            "ip": p.ip,
            "restart_count": p.restart_count,
            "labels": p.labels,
            "created_at": p.created_at.isoformat() if p.created_at else None
        }
        for p in pods
    ]

@router.get("/services")
async def get_services(
    namespace: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all services"""
    query = select(Service)
    
    if namespace:
        query = query.where(Service.namespace == namespace)
    
    query = query.order_by(Service.name)
    result = await db.execute(query)
    services = result.scalars().all()
    
    return [
        {
            "name": s.name,
            "namespace": s.namespace,
            "type": s.type,
            "cluster_ip": s.cluster_ip,
            "external_ip": s.external_ip,
            "ports": s.ports,
            "selector": s.selector
        }
        for s in services
    ]

@router.get("/deployments")
async def get_deployments(
    namespace: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all deployments"""
    query = select(Deployment)
    
    if namespace:
        query = query.where(Deployment.namespace == namespace)
    
    query = query.order_by(Deployment.name)
    result = await db.execute(query)
    deployments = result.scalars().all()
    
    return [
        {
            "name": d.name,
            "namespace": d.namespace,
            "replicas": d.replicas,
            "ready_replicas": d.ready_replicas,
            "available_replicas": d.available_replicas,
            "strategy": d.strategy,
            "image": d.image,
            "labels": d.labels
        }
        for d in deployments
    ]

@router.get("/nodes")
async def get_nodes(db: AsyncSession = Depends(get_db)):
    """Get all nodes"""
    query = select(Node).order_by(Node.name)
    result = await db.execute(query)
    nodes = result.scalars().all()
    
    return [
        {
            "name": n.name,
            "status": n.status,
            "roles": n.roles,
            "capacity_cpu": n.capacity_cpu,
            "capacity_memory": n.capacity_memory,
            "allocatable_cpu": n.allocatable_cpu,
            "allocatable_memory": n.allocatable_memory,
            "os_image": n.os_image,
            "kernel_version": n.kernel_version,
            "container_runtime": n.container_runtime
        }
        for n in nodes
    ]

@router.get("/namespaces")
async def get_namespaces(db: AsyncSession = Depends(get_db)):
    """Get all unique namespaces"""
    query = select(Pod.namespace).distinct()
    result = await db.execute(query)
    namespaces = result.scalars().all()
    return {"namespaces": sorted(namespaces)}
