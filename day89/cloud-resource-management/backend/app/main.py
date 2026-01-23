from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from pydantic import BaseModel

from .database import engine, get_db
from .models import Base, CloudResource, ResourceTag, ComplianceRule, ResourceType, ResourceState
from .services.provisioning_service import ProvisioningEngine
from .services.cost_optimizer import CostOptimizer
from .services.compliance_service import ComplianceEngine
from .services.tagging_service import TaggingService
from .services.lifecycle_service import LifecycleManager

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Cloud Resource Management System")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ProvisionRequest(BaseModel):
    name: str
    type: str
    provider: str = "aws"
    region: str = "us-east-1"
    team: str = "default"
    size: int = 1
    configuration: Dict[str, Any] = {}


class TagRequest(BaseModel):
    tags: Dict[str, str]


@app.get("/")
def health_check():
    return {"status": "healthy", "service": "Cloud Resource Management"}


@app.post("/api/resources/provision")
async def provision_resource(request: ProvisionRequest, db: Session = Depends(get_db)):
    provisioner = ProvisioningEngine(db)
    template = {
        "name": request.name,
        "type": request.type,
        "provider": request.provider,
        "region": request.region,
        "team": request.team,
        "size": request.size,
        **request.configuration,
    }
    try:
        resource = await provisioner.provision_resource(template, "user-001")
        return {
            "resource_id": resource.resource_id,
            "name": resource.name,
            "state": resource.state.value,
            "type": resource.resource_type.value,
            "provider": resource.provider,
            "region": resource.region,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/resources")
def list_resources(
    state: str = None,
    resource_type: str = None,
    team: str = None,
    db: Session = Depends(get_db),
):
    provisioner = ProvisioningEngine(db)
    filters = {}
    if state:
        filters["state"] = state
    if resource_type:
        filters["resource_type"] = resource_type
    if team:
        filters["team"] = team
    resources = provisioner.list_resources(filters)
    return [
        {
            "id": r.id,
            "resource_id": r.resource_id,
            "name": r.name,
            "type": r.resource_type.value,
            "provider": r.provider,
            "region": r.region,
            "state": r.state.value,
            "team": r.team,
            "monthly_cost": r.monthly_cost or 0,
            "cpu_utilization": r.cpu_utilization or 0,
            "created_at": r.created_at.isoformat(),
            "tag_count": len(r.tags),
        }
        for r in resources
    ]


@app.get("/api/resources/{resource_id}")
def get_resource(resource_id: str, db: Session = Depends(get_db)):
    resource = db.query(CloudResource).filter(CloudResource.resource_id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return {
        "id": resource.id,
        "resource_id": resource.resource_id,
        "name": resource.name,
        "type": resource.resource_type.value,
        "provider": resource.provider,
        "region": resource.region,
        "state": resource.state.value,
        "configuration": resource.configuration,
        "hourly_cost": resource.hourly_cost or 0,
        "monthly_cost": resource.monthly_cost or 0,
        "cpu_utilization": resource.cpu_utilization or 0,
        "memory_utilization": resource.memory_utilization or 0,
        "created_at": resource.created_at.isoformat(),
        "last_accessed": resource.last_accessed.isoformat(),
        "tags": [{"key": t.key, "value": t.value, "mandatory": t.mandatory} for t in resource.tags],
    }


@app.get("/api/cost/optimizations")
def get_cost_optimizations(db: Session = Depends(get_db)):
    optimizer = CostOptimizer(db)
    opts = optimizer.analyze_resources()
    return [
        {
            "id": o.id,
            "resource_id": o.resource_id,
            "type": o.optimization_type,
            "current_cost": o.current_cost,
            "optimized_cost": o.optimized_cost,
            "potential_savings": o.potential_savings,
            "recommendation": o.recommendation,
            "confidence": o.confidence,
            "created_at": o.created_at.isoformat(),
        }
        for o in opts
    ]


@app.get("/api/cost/summary")
def get_cost_summary(db: Session = Depends(get_db)):
    return CostOptimizer(db).get_optimization_summary()


@app.post("/api/compliance/check/{resource_id}")
def check_compliance(resource_id: int, db: Session = Depends(get_db)):
    resource = db.query(CloudResource).filter(CloudResource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    compliance = ComplianceEngine(db)
    checks = compliance.check_resource(resource)
    return [
        {
            "rule_name": c.rule.name,
            "status": c.status.value,
            "severity": c.rule.severity,
            "details": c.details,
            "remediated": c.remediated,
        }
        for c in checks
    ]


@app.get("/api/compliance/summary")
def get_compliance_summary(db: Session = Depends(get_db)):
    return ComplianceEngine(db).get_compliance_summary()


@app.post("/api/compliance/check-all")
def check_all_compliance(db: Session = Depends(get_db)):
    ComplianceEngine(db).check_all_resources()
    return {"message": "Compliance checks completed"}


@app.post("/api/resources/{resource_id}/tags")
def apply_tags(resource_id: int, request: TagRequest, db: Session = Depends(get_db)):
    try:
        TaggingService(db).apply_tags(resource_id, request.tags)
        return {"message": "Tags applied successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/tags/compliance")
def get_tag_compliance(db: Session = Depends(get_db)):
    return TaggingService(db).get_tag_compliance_summary()


@app.post("/api/tags/auto-tag")
def auto_tag_resources(db: Session = Depends(get_db)):
    TaggingService(db).auto_tag_resources()
    return {"message": "Auto-tagging completed"}


@app.get("/api/lifecycle/summary")
def get_lifecycle_summary(db: Session = Depends(get_db)):
    return LifecycleManager(db).get_lifecycle_summary()


@app.post("/api/lifecycle/check-policies")
def check_lifecycle_policies(db: Session = Depends(get_db)):
    LifecycleManager(db).check_lifecycle_policies()
    return {"message": "Lifecycle policies checked"}


@app.get("/api/stats/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_resources = db.query(CloudResource).count()
    active_resources = db.query(CloudResource).filter(CloudResource.state == ResourceState.ACTIVE).count()
    total_monthly_cost = db.query(func.sum(CloudResource.monthly_cost)).scalar() or 0
    cost_summary = CostOptimizer(db).get_optimization_summary()
    compliance_summary = ComplianceEngine(db).get_compliance_summary()
    tag_summary = TaggingService(db).get_tag_compliance_summary()
    lifecycle_summary = LifecycleManager(db).get_lifecycle_summary()
    return {
        "resources": {"total": total_resources, "active": active_resources},
        "costs": {
            "total_monthly": round(float(total_monthly_cost), 2),
            "potential_savings": cost_summary["total_potential_savings"],
        },
        "compliance": {
            "rate": compliance_summary["compliance_rate"],
            "total_checks": compliance_summary["total_checks"],
        },
        "tags": {"compliance_rate": tag_summary["compliance_rate"]},
        "lifecycle": lifecycle_summary,
    }
