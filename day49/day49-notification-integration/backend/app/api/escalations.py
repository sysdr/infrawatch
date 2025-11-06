from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.models import EscalationPolicy, AlertSeverity
from pydantic import BaseModel
from typing import List, Dict

router = APIRouter()

class EscalationPolicyCreate(BaseModel):
    service_name: str
    severity: AlertSeverity
    policy_config: List[Dict]  # [{level: 0, users: [...], timeout_minutes: 5}]

@router.post("/")
async def create_policy(policy_data: EscalationPolicyCreate, db: AsyncSession = Depends(get_db)):
    """Create escalation policy"""
    try:
        policy = EscalationPolicy(
            service_name=policy_data.service_name,
            severity=policy_data.severity,
            policy_config=policy_data.policy_config
        )
        db.add(policy)
        await db.commit()
        
        return {"message": "Escalation policy created"}
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error creating escalation policy: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create policy: {str(e)}")

@router.get("/")
async def list_policies(db: AsyncSession = Depends(get_db)):
    """List escalation policies"""
    try:
        result = await db.execute(select(EscalationPolicy))
        policies = result.scalars().all()
        
        return [
            {
                "id": p.id,
                "service_name": p.service_name,
                "severity": p.severity.value if hasattr(p.severity, 'value') else str(p.severity),
                "policy_config": p.policy_config if isinstance(p.policy_config, list) else []
            }
            for p in policies
        ]
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error listing escalation policies: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list policies: {str(e)}")
