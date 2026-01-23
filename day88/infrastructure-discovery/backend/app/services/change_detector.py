from datetime import datetime, timedelta
from typing import List, Dict
from sqlalchemy import select, and_
from app.models.resource import Resource, Change
from app.utils.database import AsyncSessionLocal
from app.utils.redis_client import redis_client
import json

class ChangeDetector:
    def __init__(self):
        self.baseline_established = {}
    
    async def detect_changes(self, current_resources: List[Dict]) -> List[Dict]:
        """Detect changes in discovered resources"""
        changes = []
        
        async with AsyncSessionLocal() as session:
            # Get all current resource IDs
            current_ids = {r["id"] for r in current_resources}
            
            # Check database for existing resources
            result = await session.execute(select(Resource))
            db_resources = result.scalars().all()
            db_ids = {r.id for r in db_resources}
            
            # Detect new resources (CREATED)
            new_ids = current_ids - db_ids
            for resource in current_resources:
                if resource["id"] in new_ids:
                    change = Change(
                        resource_id=resource["id"],
                        change_type="CREATED",
                        new_hash=self.calculate_hash(resource),
                        diff={"action": "created", "resource": resource}
                    )
                    session.add(change)
                    changes.append({
                        "resource_id": resource["id"],
                        "type": "CREATED",
                        "timestamp": datetime.utcnow().isoformat()
                    })
            
            # Detect deleted resources
            deleted_ids = db_ids - current_ids
            for resource in db_resources:
                if resource.id in deleted_ids:
                    change = Change(
                        resource_id=resource.id,
                        change_type="DELETED",
                        old_hash=resource.config_hash,
                        diff={"action": "deleted", "resource_id": resource.id}
                    )
                    session.add(change)
                    changes.append({
                        "resource_id": resource.id,
                        "type": "DELETED",
                        "timestamp": datetime.utcnow().isoformat()
                    })
            
            # Detect modifications
            for resource in current_resources:
                if resource["id"] in db_ids:
                    db_resource = next(r for r in db_resources if r.id == resource["id"])
                    current_hash = self.calculate_hash(resource)
                    
                    if db_resource.config_hash != current_hash:
                        change = Change(
                            resource_id=resource["id"],
                            change_type="MODIFIED",
                            old_hash=db_resource.config_hash,
                            new_hash=current_hash,
                            diff=self.calculate_diff(db_resource.resource_metadata, resource)
                        )
                        session.add(change)
                        changes.append({
                            "resource_id": resource["id"],
                            "type": "MODIFIED",
                            "timestamp": datetime.utcnow().isoformat()
                        })
            
            await session.commit()
            
            # Store changes in Redis for time-series analysis
            if changes:
                timestamp = datetime.utcnow().timestamp()
                await redis_client.zadd(
                    "changes:timeline",
                    {json.dumps(c): timestamp for c in changes}
                )
                
                # Increment change counters
                for change in changes:
                    await redis_client.hincrby(
                        "changes:stats",
                        change["type"]
                    )
        
        return changes
    
    def calculate_hash(self, config: dict) -> str:
        import hashlib
        config_str = json.dumps(config, sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()
    
    def calculate_diff(self, old_config: dict, new_config: dict) -> dict:
        """Calculate differences between configurations"""
        diff = {"changed_fields": []}
        
        all_keys = set(old_config.keys()) | set(new_config.keys())
        for key in all_keys:
            old_val = old_config.get(key)
            new_val = new_config.get(key)
            
            if old_val != new_val:
                diff["changed_fields"].append({
                    "field": key,
                    "old": old_val,
                    "new": new_val
                })
        
        return diff
