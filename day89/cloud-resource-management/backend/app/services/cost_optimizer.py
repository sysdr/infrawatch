from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models import CloudResource, CostOptimization, ResourceType, ResourceState

class CostOptimizer:
    def __init__(self, db: Session):
        self.db = db

    def analyze_resources(self) -> List[CostOptimization]:
        optimizations = []
        resources = self.db.query(CloudResource).filter(
            CloudResource.state == ResourceState.ACTIVE
        ).all()

        for resource in resources:
            if self._is_oversized(resource):
                opt = self._create_rightsizing_recommendation(resource)
                optimizations.append(opt)
            if self._is_idle(resource):
                opt = self._create_idle_recommendation(resource)
                optimizations.append(opt)
            if resource.resource_type == ResourceType.COMPUTE and resource.team != "production":
                opt = self._create_schedule_recommendation(resource)
                optimizations.append(opt)
        return optimizations

    def _is_oversized(self, resource: CloudResource) -> bool:
        if resource.resource_type == ResourceType.COMPUTE:
            return (resource.cpu_utilization or 0) < 15 and (resource.memory_utilization or 0) < 20
        return False

    def _is_idle(self, resource: CloudResource) -> bool:
        idle_threshold = datetime.utcnow() - timedelta(days=7)
        return (resource.last_accessed < idle_threshold and (resource.cpu_utilization or 0) < 5)

    def _create_rightsizing_recommendation(self, resource: CloudResource) -> CostOptimization:
        current_cost = resource.monthly_cost or 0
        optimized_cost = current_cost * 0.5
        opt = CostOptimization(
            resource_id=resource.id,
            optimization_type="right_sizing",
            current_cost=current_cost,
            optimized_cost=optimized_cost,
            potential_savings=current_cost - optimized_cost,
            recommendation=f"Downsize {resource.name}. CPU {resource.cpu_utilization or 0}%, Memory {resource.memory_utilization or 0}%",
            confidence=0.85
        )
        self.db.add(opt)
        self.db.commit()
        return opt

    def _create_idle_recommendation(self, resource: CloudResource) -> CostOptimization:
        current_cost = resource.monthly_cost or 0
        opt = CostOptimization(
            resource_id=resource.id,
            optimization_type="idle_resource",
            current_cost=current_cost,
            optimized_cost=0,
            potential_savings=current_cost,
            recommendation=f"Resource {resource.name} appears idle. Consider terminating to save ${current_cost:.2f}/month",
            confidence=0.92
        )
        self.db.add(opt)
        self.db.commit()
        return opt

    def _create_schedule_recommendation(self, resource: CloudResource) -> CostOptimization:
        current_cost = resource.monthly_cost or 0
        optimized_cost = current_cost * 0.5
        savings = current_cost - optimized_cost
        opt = CostOptimization(
            resource_id=resource.id,
            optimization_type="schedule_based",
            current_cost=current_cost,
            optimized_cost=optimized_cost,
            potential_savings=savings,
            recommendation=f"Stop {resource.name} during off-hours. Potential savings: ${savings:.2f}/month",
            confidence=0.78
        )
        self.db.add(opt)
        self.db.commit()
        return opt

    def get_optimization_summary(self) -> Dict[str, Any]:
        optimizations = self.db.query(CostOptimization).filter(CostOptimization.applied == False).all()
        total = sum(opt.potential_savings for opt in optimizations)
        by_type = {}
        for opt in optimizations:
            t = opt.optimization_type
            if t not in by_type:
                by_type[t] = {"count": 0, "savings": 0}
            by_type[t]["count"] += 1
            by_type[t]["savings"] += opt.potential_savings
        return {
            "total_recommendations": len(optimizations),
            "total_potential_savings": round(total, 2),
            "by_type": by_type
        }
