from typing import Dict, List, Any
from datetime import datetime
import json
import uuid
import asyncio
from sqlalchemy.orm import Session
from ..models import CloudResource, ResourceState, ResourceType, LifecycleEvent
from ..database import SessionLocal
from ..cache import cache

class ProvisioningEngine:
    def __init__(self, db: Session):
        self.db = db

    async def provision_resource(self, template: Dict[str, Any], owner_id: str) -> CloudResource:
        resource_id = f"res-{uuid.uuid4().hex[:12]}"
        validation_result = await self._validate_template(template)
        if not validation_result["valid"]:
            raise ValueError(f"Invalid template: {validation_result['errors']}")

        hourly = self._calculate_hourly_cost(template)
        monthly = round(hourly * 730, 2)

        resource = CloudResource(
            resource_id=resource_id,
            name=template.get("name", "unnamed-resource"),
            resource_type=ResourceType[template["type"].upper()],
            provider=template.get("provider", "aws"),
            region=template.get("region", "us-east-1"),
            state=ResourceState.VALIDATING,
            configuration=template,
            template=json.dumps(template),
            owner_id=owner_id,
            team=template.get("team", "default"),
            hourly_cost=hourly,
            monthly_cost=monthly,
        )

        self.db.add(resource)
        self.db.commit()
        self.db.refresh(resource)

        event = LifecycleEvent(
            resource_id=resource.id,
            event_type="provisioning_started",
            to_state="validating",
            details={"template": template}
        )
        self.db.add(event)
        self.db.commit()

        asyncio.create_task(self._provision_async(resource.id))
        return resource

    async def _validate_template(self, template: Dict[str, Any]) -> Dict[str, Any]:
        errors = []
        for field in ["name", "type", "provider"]:
            if field not in template:
                errors.append(f"Missing required field: {field}")
        if template.get("type") not in ["compute", "storage", "database", "network", "container"]:
            errors.append(f"Invalid resource type: {template.get('type')}")
        return {"valid": len(errors) == 0, "errors": errors}

    async def _provision_async(self, resource_id: int):
        await asyncio.sleep(1)
        db = SessionLocal()
        try:
            resource = db.query(CloudResource).filter(CloudResource.id == resource_id).first()
            if not resource:
                return
            resource.state = ResourceState.PROVISIONING
            db.commit()
            await asyncio.sleep(1)
            resource.state = ResourceState.ACTIVE
            resource.updated_at = datetime.utcnow()
            db.commit()
            try:
                cache.delete(f"resource:{resource.resource_id}")
            except Exception:
                pass
        finally:
            db.close()

    def _calculate_hourly_cost(self, template: Dict[str, Any]) -> float:
        cost_map = {"compute": 0.15, "storage": 0.02, "database": 0.25, "network": 0.05, "container": 0.08}
        base = cost_map.get(template["type"], 0.10)
        return base * template.get("size", 1)

    def list_resources(self, filters: Dict[str, Any] = None) -> List[CloudResource]:
        query = self.db.query(CloudResource)
        if filters:
            if "state" in filters:
                query = query.filter(CloudResource.state == ResourceState[filters["state"].upper()])
            if "resource_type" in filters:
                query = query.filter(CloudResource.resource_type == ResourceType[filters["resource_type"].upper()])
            if "owner_id" in filters:
                query = query.filter(CloudResource.owner_id == filters["owner_id"])
            if "team" in filters:
                query = query.filter(CloudResource.team == filters["team"])
        return query.all()
