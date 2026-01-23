import asyncio
import aiohttp
import hashlib
import json
from datetime import datetime
from typing import List, Dict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resource import Resource, Relationship
from app.utils.database import AsyncSessionLocal
from app.utils.redis_client import redis_client

class MockCloudProvider:
    """Simulates AWS/Cloud provider APIs"""
    
    async def describe_instances(self):
        return [
            {
                "id": f"i-{i:08x}",
                "type": "instance",
                "name": f"web-server-{i}",
                "instance_type": "t3.medium",
                "state": "running",
                "security_groups": [f"sg-{(i % 3):08x}"],
                "subnet": f"subnet-{(i % 2):08x}",
                "region": "us-east-1"
            }
            for i in range(20)
        ]
    
    async def describe_load_balancers(self):
        return [
            {
                "id": f"lb-{i:08x}",
                "type": "load_balancer",
                "name": f"main-lb-{i}",
                "scheme": "internet-facing",
                "instances": [f"i-{j:08x}" for j in range(i*5, (i+1)*5)],
                "region": "us-east-1"
            }
            for i in range(4)
        ]
    
    async def describe_databases(self):
        return [
            {
                "id": f"db-{i:08x}",
                "type": "database",
                "name": f"postgres-{i}",
                "engine": "postgres",
                "version": "14.5",
                "instance_class": "db.t3.medium",
                "security_groups": [f"sg-{(i % 3):08x}"],
                "region": "us-east-1"
            }
            for i in range(5)
        ]
    
    async def describe_security_groups(self):
        return [
            {
                "id": f"sg-{i:08x}",
                "type": "security_group",
                "name": f"app-sg-{i}",
                "vpc": "vpc-00000001",
                "rules": [
                    {"protocol": "tcp", "port": 80, "source": "0.0.0.0/0"},
                    {"protocol": "tcp", "port": 443, "source": "0.0.0.0/0"}
                ],
                "region": "us-east-1"
            }
            for i in range(3)
        ]

class DiscoveryEngine:
    def __init__(self):
        self.provider = MockCloudProvider()
        self.discovered_resources = {}
    
    def calculate_hash(self, config: dict) -> str:
        """Calculate configuration hash"""
        config_str = json.dumps(config, sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()
    
    async def discover_resources(self, resource_type: str) -> List[Dict]:
        """Discover resources of specific type"""
        if resource_type == "instance":
            return await self.provider.describe_instances()
        elif resource_type == "load_balancer":
            return await self.provider.describe_load_balancers()
        elif resource_type == "database":
            return await self.provider.describe_databases()
        elif resource_type == "security_group":
            return await self.provider.describe_security_groups()
        return []
    
    async def store_resource(self, resource_data: Dict, session: AsyncSession):
        """Store discovered resource"""
        config_hash = self.calculate_hash(resource_data)
        
        # Check if resource exists
        result = await session.execute(
            select(Resource).where(Resource.id == resource_data["id"])
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            # Update if hash changed
            if existing.config_hash != config_hash:
                existing.config_hash = config_hash
                existing.resource_metadata = resource_data
                existing.updated_at = datetime.utcnow()
                existing.state = "MODIFIED"
        else:
            # Create new resource
            resource = Resource(
                id=resource_data["id"],
                resource_type=resource_data["type"],
                name=resource_data["name"],
                provider="aws",
                region=resource_data.get("region", "us-east-1"),
                resource_metadata=resource_data,
                config_hash=config_hash,
                state="DISCOVERED"
            )
            session.add(resource)
        
        await session.commit()
        return config_hash
    
    async def extract_relationships(self, resource_data: Dict, session: AsyncSession):
        """Extract and store relationships"""
        source_id = resource_data["id"]
        relationships = []
        
        # Extract relationships based on resource type
        if resource_data["type"] == "instance":
            # Instance -> Security Group
            for sg in resource_data.get("security_groups", []):
                relationships.append({
                    "source_id": source_id,
                    "target_id": sg,
                    "relationship_type": "uses_security_group"
                })
        
        elif resource_data["type"] == "load_balancer":
            # Load Balancer -> Instances
            for instance in resource_data.get("instances", []):
                relationships.append({
                    "source_id": source_id,
                    "target_id": instance,
                    "relationship_type": "forwards_to"
                })
        
        elif resource_data["type"] == "database":
            # Database -> Security Group
            for sg in resource_data.get("security_groups", []):
                relationships.append({
                    "source_id": source_id,
                    "target_id": sg,
                    "relationship_type": "protected_by"
                })
        
        # Store relationships
        for rel_data in relationships:
            # Check if relationship exists
            result = await session.execute(
                select(Relationship).where(
                    Relationship.source_id == rel_data["source_id"],
                    Relationship.target_id == rel_data["target_id"],
                    Relationship.relationship_type == rel_data["relationship_type"]
                )
            )
            existing_rel = result.scalar_one_or_none()
            
            if not existing_rel:
                rel = Relationship(**rel_data)
                session.add(rel)
        
        await session.commit()
    
    async def discover_all(self) -> List[Dict]:
        """Discover all resource types"""
        resource_types = ["instance", "load_balancer", "database", "security_group"]
        all_resources = []
        
        async with AsyncSessionLocal() as session:
            for rtype in resource_types:
                try:
                    resources = await self.discover_resources(rtype)
                    
                    for resource in resources:
                        await self.store_resource(resource, session)
                        await self.extract_relationships(resource, session)
                        all_resources.append(resource)
                    
                    # Cache in Redis
                    await redis_client.set(
                        f"discovery:{rtype}:last_scan",
                        datetime.utcnow().isoformat(),
                        ex=3600
                    )
                    
                except Exception as e:
                    print(f"Error discovering {rtype}: {e}")
        
        return all_resources
