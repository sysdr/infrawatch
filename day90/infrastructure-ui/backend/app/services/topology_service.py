import math
from typing import List, Dict, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.resource import Resource, ResourceDependency, Metric
import random

class TopologyService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_topology(self, filters: dict = None) -> Dict:
        """Calculate and return topology graph"""
        # Fetch resources
        query = select(Resource)
        if filters:
            if filters.get('cloud_provider'):
                query = query.where(Resource.cloud_provider == filters['cloud_provider'])
            if filters.get('region'):
                query = query.where(Resource.region == filters['region'])
        
        result = await self.db.execute(query)
        resources = result.scalars().all()
        
        # Fetch dependencies
        resource_ids = [r.id for r in resources]
        dep_query = select(ResourceDependency).where(
            ResourceDependency.source_id.in_(resource_ids),
            ResourceDependency.target_id.in_(resource_ids)
        )
        dep_result = await self.db.execute(dep_query)
        dependencies = dep_result.scalars().all()
        
        # Get latest metrics for health status
        metrics_map = await self._get_latest_metrics(resource_ids)
        
        # Calculate layout
        nodes = []
        for resource in resources:
            health = self._calculate_health(metrics_map.get(resource.id))
            nodes.append({
                'id': resource.id,
                'type': resource.resource_type,
                'name': resource.name,
                'status': resource.status,
                'health': health,
                'provider': resource.cloud_provider,
                'region': resource.region,
                'tags': resource.tags,
                'position': None  # Will be calculated
            })
        
        edges = []
        for dep in dependencies:
            edges.append({
                'source': dep.source_id,
                'target': dep.target_id,
                'type': dep.dependency_type,
                'strength': dep.strength
            })
        
        # Calculate positions using force-directed layout
        positions = self._calculate_layout(nodes, edges)
        for node in nodes:
            node['position'] = positions[node['id']]
        
        return {
            'nodes': nodes,
            'edges': edges,
            'stats': {
                'total_resources': len(nodes),
                'total_connections': len(edges),
                'healthy': len([n for n in nodes if n['health'] == 'green']),
                'warning': len([n for n in nodes if n['health'] == 'yellow']),
                'critical': len([n for n in nodes if n['health'] == 'red'])
            }
        }
    
    async def _get_latest_metrics(self, resource_ids: List[str]) -> Dict:
        """Get most recent metrics for each resource"""
        from sqlalchemy import and_, func
        
        # Subquery to get latest timestamp per resource
        subq = select(
            Metric.resource_id,
            func.max(Metric.timestamp).label('max_ts')
        ).where(
            Metric.resource_id.in_(resource_ids)
        ).group_by(Metric.resource_id).subquery()
        
        # Join to get full metric data
        query = select(Metric).join(
            subq,
            and_(
                Metric.resource_id == subq.c.resource_id,
                Metric.timestamp == subq.c.max_ts
            )
        )
        
        result = await self.db.execute(query)
        metrics = result.scalars().all()
        
        return {m.resource_id: m for m in metrics}
    
    def _calculate_health(self, metric) -> str:
        """Calculate health status from metrics"""
        if not metric:
            return 'gray'
        
        if metric.cpu_usage > 85 or metric.memory_usage > 90 or metric.error_rate > 5:
            return 'red'
        elif metric.cpu_usage > 70 or metric.memory_usage > 80 or metric.error_rate > 1:
            return 'yellow'
        else:
            return 'green'
    
    def _calculate_layout(self, nodes: List[Dict], edges: List[Dict], iterations: int = 100) -> Dict[str, Tuple[float, float]]:
        """Force-directed graph layout algorithm"""
        if not nodes:
            return {}
        
        # Initialize random positions
        positions = {}
        for node in nodes:
            positions[node['id']] = (
                random.uniform(0, 800),
                random.uniform(0, 600)
            )
        
        # Build adjacency map
        adjacency = {node['id']: [] for node in nodes}
        for edge in edges:
            adjacency[edge['source']].append(edge['target'])
            adjacency[edge['target']].append(edge['source'])
        
        k = 50  # Optimal distance
        area = 800 * 600
        k = math.sqrt(area / len(nodes))
        
        for iteration in range(iterations):
            forces = {node_id: [0.0, 0.0] for node_id in positions}
            
            # Repulsive forces between all pairs
            for i, node1 in enumerate(nodes):
                for node2 in nodes[i+1:]:
                    dx = positions[node1['id']][0] - positions[node2['id']][0]
                    dy = positions[node1['id']][1] - positions[node2['id']][1]
                    distance = math.sqrt(dx*dx + dy*dy) + 0.01
                    
                    force = (k * k) / distance
                    fx = (dx / distance) * force
                    fy = (dy / distance) * force
                    
                    forces[node1['id']][0] += fx
                    forces[node1['id']][1] += fy
                    forces[node2['id']][0] -= fx
                    forces[node2['id']][1] -= fy
            
            # Attractive forces for connected nodes
            for edge in edges:
                dx = positions[edge['source']][0] - positions[edge['target']][0]
                dy = positions[edge['source']][1] - positions[edge['target']][1]
                distance = math.sqrt(dx*dx + dy*dy) + 0.01
                
                force = (distance * distance) / k
                fx = (dx / distance) * force
                fy = (dy / distance) * force
                
                forces[edge['source']][0] -= fx
                forces[edge['source']][1] -= fy
                forces[edge['target']][0] += fx
                forces[edge['target']][1] += fy
            
            # Update positions
            max_displacement = 0
            for node_id, force in forces.items():
                displacement = math.sqrt(force[0]*force[0] + force[1]*force[1])
                if displacement > 0:
                    # Limit displacement
                    limited = min(displacement, k / 2)
                    positions[node_id] = (
                        positions[node_id][0] + (force[0] / displacement) * limited * 0.9,
                        positions[node_id][1] + (force[1] / displacement) * limited * 0.9
                    )
                    max_displacement = max(max_displacement, limited)
            
            # Check convergence
            if max_displacement < 0.1:
                break
        
        # Normalize positions to fit in canvas
        if positions:
            xs = [pos[0] for pos in positions.values()]
            ys = [pos[1] for pos in positions.values()]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            
            width_range = max_x - min_x if max_x > min_x else 1
            height_range = max_y - min_y if max_y > min_y else 1
            
            for node_id in positions:
                x = ((positions[node_id][0] - min_x) / width_range) * 700 + 50
                y = ((positions[node_id][1] - min_y) / height_range) * 500 + 50
                positions[node_id] = (round(x, 2), round(y, 2))
        
        return positions
