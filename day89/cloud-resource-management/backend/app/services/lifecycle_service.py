from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models import CloudResource, LifecyclePolicy, LifecycleEvent, ResourceState, ResourceType

class LifecycleManager:
    def __init__(self, db: Session):
        self.db = db
        self._init_default_policies()

    def _init_default_policies(self):
        for pd in [
            {"name": "production_compute", "resource_type": ResourceType.COMPUTE, "environment": "production",
             "idle_threshold_days": 30, "deletion_after_days": 90, "notification_days": [7, 3, 1], "require_approval": True},
            {"name": "dev_compute", "resource_type": ResourceType.COMPUTE, "environment": "development",
             "idle_threshold_days": 7, "deletion_after_days": 14, "notification_days": [3, 1], "require_approval": False},
            {"name": "production_storage", "resource_type": ResourceType.STORAGE, "environment": "production",
             "idle_threshold_days": 60, "deletion_after_days": 180, "notification_days": [14, 7, 3], "require_approval": True},
        ]:
            if not self.db.query(LifecyclePolicy).filter(LifecyclePolicy.name == pd["name"]).first():
                self.db.add(LifecyclePolicy(**pd))
        self.db.commit()

    def check_lifecycle_policies(self):
        for policy in self.db.query(LifecyclePolicy).filter(LifecyclePolicy.enabled == True).all():
            for r in self.db.query(CloudResource).filter(
                CloudResource.resource_type == policy.resource_type,
                CloudResource.state == ResourceState.ACTIVE
            ).all():
                env = next((t.value for t in r.tags if t.key == "Environment"), None)
                if env != policy.environment:
                    continue
                self._apply(r, policy)

    def _apply(self, resource: CloudResource, policy: LifecyclePolicy):
        now = datetime.utcnow()
        if (now - resource.last_accessed).days >= policy.idle_threshold_days and resource.state == ResourceState.ACTIVE:
            self._transition_idle(resource)
        if (now - resource.created_at).days >= policy.deletion_after_days:
            self._schedule_deletion(resource, policy)

    def _transition_idle(self, resource: CloudResource):
        if resource.state == ResourceState.IDLE:
            return
        old = resource.state
        resource.state = ResourceState.IDLE
        self.db.add(LifecycleEvent(resource_id=resource.id, event_type="state_change", from_state=old.value, to_state=ResourceState.IDLE.value, details={"reason": "idle"}))
        self.db.commit()

    def _schedule_deletion(self, resource: CloudResource, policy: LifecyclePolicy):
        if resource.scheduled_deletion:
            return
        from_state = resource.state.value
        deletion_date = datetime.utcnow() + timedelta(days=7)
        resource.scheduled_deletion = deletion_date
        resource.state = ResourceState.DEPRECATED
        self.db.add(LifecycleEvent(
            resource_id=resource.id, event_type="deletion_scheduled",
            from_state=from_state, to_state=ResourceState.DEPRECATED.value,
            details={"scheduled_deletion": deletion_date.isoformat(), "policy": policy.name, "require_approval": policy.require_approval}
        ))
        self.db.commit()

    def get_lifecycle_summary(self) -> Dict[str, Any]:
        resources = self.db.query(CloudResource).all()
        state_counts = {}
        for r in resources:
            s = r.state.value
            state_counts[s] = state_counts.get(s, 0) + 1
        scheduled = self.db.query(CloudResource).filter(CloudResource.scheduled_deletion.isnot(None)).count()
        return {"total_resources": len(resources), "state_distribution": state_counts, "scheduled_deletions": scheduled}
