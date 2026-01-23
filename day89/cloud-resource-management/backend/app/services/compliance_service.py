from typing import List, Dict, Any
from sqlalchemy.orm import Session
from ..models import (
    CloudResource,
    ComplianceRule,
    ComplianceCheck,
    ComplianceStatus,
    ResourceType,
    ResourceState,
)


class ComplianceEngine:
    def __init__(self, db: Session):
        self.db = db
        self._init_default_rules()

    def _init_default_rules(self):
        default_rules = [
            {
                "name": "encryption_at_rest",
                "description": "Storage encryption at rest",
                "resource_type": ResourceType.STORAGE,
                "severity": "critical",
                "condition": {"encryption_enabled": True},
                "remediation": "Enable KMS",
                "auto_remediate": False,
            },
            {
                "name": "public_access_blocked",
                "description": "Block public access",
                "resource_type": ResourceType.STORAGE,
                "severity": "high",
                "condition": {"public_access": False},
                "remediation": "Update ACL",
                "auto_remediate": True,
            },
            {
                "name": "backup_enabled",
                "description": "DB backups",
                "resource_type": ResourceType.DATABASE,
                "severity": "high",
                "condition": {"backup_enabled": True},
                "remediation": "Enable backups",
                "auto_remediate": False,
            },
            {
                "name": "multi_az_enabled",
                "description": "Multi-AZ",
                "resource_type": ResourceType.DATABASE,
                "severity": "medium",
                "condition": {"multi_az": True, "environment": "production"},
                "remediation": "Multi-AZ",
                "auto_remediate": False,
            },
            {
                "name": "security_group_rules",
                "description": "Restrictive SGs",
                "resource_type": ResourceType.NETWORK,
                "severity": "critical",
                "condition": {"unrestricted_access": False},
                "remediation": "Update SGs",
                "auto_remediate": True,
            },
        ]
        for rd in default_rules:
            if not self.db.query(ComplianceRule).filter(ComplianceRule.name == rd["name"]).first():
                self.db.add(ComplianceRule(**rd))
        self.db.commit()

    def check_resource(self, resource: CloudResource) -> List[ComplianceCheck]:
        rules = self.db.query(ComplianceRule).filter(
            ComplianceRule.resource_type == resource.resource_type,
            ComplianceRule.enabled == True,
        ).all()
        checks = []
        for rule in rules:
            status, details = self._evaluate_rule(resource, rule)
            check = ComplianceCheck(
                resource_id=resource.id,
                rule_id=rule.id,
                status=status,
                details=details,
            )
            self.db.add(check)
            checks.append(check)
            if status == ComplianceStatus.NON_COMPLIANT and rule.auto_remediate:
                self._auto_remediate(resource, rule, check)
        self.db.commit()
        return checks

    def _evaluate_rule(self, resource: CloudResource, rule: ComplianceRule):
        config = resource.configuration or {}
        condition = rule.condition or {}
        is_compliant = True
        details = {}
        for k, v in condition.items():
            actual = config.get(k)
            details[k] = {"expected": v, "actual": actual, "matches": actual == v}
            if actual != v:
                is_compliant = False
        status = ComplianceStatus.COMPLIANT if is_compliant else ComplianceStatus.NON_COMPLIANT
        return status, details

    def _auto_remediate(self, resource: CloudResource, rule: ComplianceRule, check: ComplianceCheck):
        check.remediated = True
        check.remediation_details = f"Auto-remediated: {rule.remediation}"
        if resource.configuration and rule.condition:
            for k, v in rule.condition.items():
                resource.configuration[k] = v
        self.db.commit()

    def get_compliance_summary(self) -> Dict[str, Any]:
        total = self.db.query(CloudResource).count()
        checks = self.db.query(ComplianceCheck).all()
        status_counts = {"compliant": 0, "non_compliant": 0, "warning": 0}
        for c in checks:
            if c.status == ComplianceStatus.COMPLIANT:
                status_counts["compliant"] += 1
            elif c.status == ComplianceStatus.NON_COMPLIANT:
                status_counts["non_compliant"] += 1
            else:
                status_counts["warning"] += 1
        rate = (status_counts["compliant"] / len(checks) * 100) if checks else 0
        return {
            "total_resources": total,
            "total_checks": len(checks),
            "compliance_rate": round(rate, 2),
            "status_counts": status_counts,
        }

    def check_all_resources(self):
        resources = self.db.query(CloudResource).filter(
            CloudResource.state == ResourceState.ACTIVE
        ).all()
        for r in resources:
            self.check_resource(r)
