from typing import List, Dict
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.resource import Resource, ResourceDependency, Metric, Cost
from datetime import datetime, timedelta
import uuid

class ResourceService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def list_resources(self, filters: dict = None, limit: int = 100, offset: int = 0) -> Dict:
        """List resources with pagination and filtering"""
        query = select(Resource)
        
        if filters:
            if filters.get('resource_type'):
                query = query.where(Resource.resource_type == filters['resource_type'])
            if filters.get('cloud_provider'):
                query = query.where(Resource.cloud_provider == filters['cloud_provider'])
            if filters.get('status'):
                query = query.where(Resource.status == filters['status'])
            if filters.get('search'):
                query = query.where(Resource.name.ilike(f"%{filters['search']}%"))
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Get paginated results
        query = query.order_by(Resource.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(query)
        resources = result.scalars().all()
        
        return {
            'items': [self._resource_to_dict(r) for r in resources],
            'total': total,
            'limit': limit,
            'offset': offset
        }
    
    async def get_resource(self, resource_id: str) -> Dict:
        """Get single resource with details"""
        query = select(Resource).where(Resource.id == resource_id)
        result = await self.db.execute(query)
        resource = result.scalar_one_or_none()
        
        if not resource:
            return None
        
        # Get dependencies
        dep_query = select(ResourceDependency).where(
            (ResourceDependency.source_id == resource_id) |
            (ResourceDependency.target_id == resource_id)
        )
        dep_result = await self.db.execute(dep_query)
        dependencies = dep_result.scalars().all()
        
        # Get recent metrics
        metrics_query = select(Metric).where(
            Metric.resource_id == resource_id
        ).order_by(Metric.timestamp.desc()).limit(20)
        metrics_result = await self.db.execute(metrics_query)
        metrics = metrics_result.scalars().all()
        
        # Get cost summary
        cost_query = select(func.sum(Cost.amount)).where(
            Cost.resource_id == resource_id,
            Cost.date >= datetime.utcnow() - timedelta(days=30)
        )
        cost_result = await self.db.execute(cost_query)
        monthly_cost = cost_result.scalar() or 0.0
        
        resource_dict = self._resource_to_dict(resource)
        resource_dict['dependencies'] = [
            {'source': d.source_id, 'target': d.target_id, 'type': d.dependency_type}
            for d in dependencies
        ]
        resource_dict['metrics'] = [
            {
                'timestamp': m.timestamp.isoformat(),
                'cpu': m.cpu_usage,
                'memory': m.memory_usage,
                'network_in': m.network_in,
                'network_out': m.network_out
            }
            for m in metrics
        ]
        resource_dict['monthly_cost'] = round(monthly_cost, 2)
        
        return resource_dict
    
    async def create_resource(self, data: Dict) -> Dict:
        """Create new resource"""
        resource = Resource(
            id=str(uuid.uuid4()),
            resource_type=data['resource_type'],
            cloud_provider=data['cloud_provider'],
            region=data['region'],
            name=data['name'],
            status='provisioning',
            tags=data.get('tags', {}),
            config=data.get('config', {})
        )
        
        self.db.add(resource)
        await self.db.flush()
        
        # Simulate provisioning with initial metric
        metric = Metric(
            resource_id=resource.id,
            cpu_usage=10.0,
            memory_usage=20.0
        )
        self.db.add(metric)
        
        return self._resource_to_dict(resource)
    
    async def update_resource(self, resource_id: str, data: Dict) -> Dict:
        """Update resource"""
        query = select(Resource).where(Resource.id == resource_id)
        result = await self.db.execute(query)
        resource = result.scalar_one_or_none()
        
        if not resource:
            return None
        
        if 'name' in data:
            resource.name = data['name']
        if 'status' in data:
            resource.status = data['status']
        if 'tags' in data:
            resource.tags = data['tags']
        if 'config' in data:
            resource.config = data['config']
        
        resource.updated_at = datetime.utcnow()
        await self.db.flush()
        
        return self._resource_to_dict(resource)
    
    async def delete_resource(self, resource_id: str) -> bool:
        """Delete resource"""
        query = delete(Resource).where(Resource.id == resource_id)
        result = await self.db.execute(query)
        return result.rowcount > 0
    
    def _resource_to_dict(self, resource: Resource) -> Dict:
        return {
            'id': resource.id,
            'type': resource.resource_type,
            'provider': resource.cloud_provider,
            'region': resource.region,
            'name': resource.name,
            'status': resource.status,
            'tags': resource.tags,
            'config': resource.config,
            'created_at': resource.created_at.isoformat(),
            'updated_at': resource.updated_at.isoformat()
        }
