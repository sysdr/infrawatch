from typing import List, Dict, Any
from sqlalchemy.orm import Session
from ..models import CloudResource, ResourceTag

class TaggingService:
    MANDATORY_TAGS = ["Environment", "Owner", "CostCenter", "Application", "Project"]

    def __init__(self, db: Session):
        self.db = db

    def apply_tags(self, resource_id: int, tags: Dict[str, str], auto_applied: bool = False):
        r = self.db.query(CloudResource).filter(CloudResource.id == resource_id).first()
        if not r:
            raise ValueError(f"Resource {resource_id} not found")
        for k, v in tags.items():
            self.db.add(ResourceTag(resource_id=resource_id, key=k, value=v, mandatory=k in self.MANDATORY_TAGS, auto_applied=auto_applied))
        self.db.commit()

    def validate_tags(self, resource: CloudResource) -> Dict[str, Any]:
        existing = {t.key: t.value for t in resource.tags}
        missing = [t for t in self.MANDATORY_TAGS if t not in existing]
        return {"compliant": len(missing) == 0, "missing_tags": missing, "existing_tags": existing}

    def auto_tag_resources(self):
        for r in self.db.query(CloudResource).all():
            v = self.validate_tags(r)
            if not v["compliant"]:
                auto = {}
                if "Environment" in v["missing_tags"]:
                    auto["Environment"] = self._infer_env(r)
                if "Application" in v["missing_tags"]:
                    auto["Application"] = (r.name.split("-")[0] if "-" in r.name else "unknown")
                if auto:
                    self.apply_tags(r.id, auto, auto_applied=True)

    def _infer_env(self, r: CloudResource) -> str:
        n = r.name.lower()
        if "prod" in n or "production" in n:
            return "production"
        if "staging" in n or "stg" in n:
            return "staging"
        if "dev" in n or "development" in n:
            return "development"
        return "unknown"

    def get_tag_compliance_summary(self) -> Dict[str, Any]:
        resources = self.db.query(CloudResource).all()
        total = len(resources)
        compliant = sum(1 for r in resources if self.validate_tags(r)["compliant"])
        rate = (compliant / total * 100) if total else 0
        return {"total_resources": total, "compliant_resources": compliant, "non_compliant_resources": total - compliant, "compliance_rate": round(rate, 2)}
