#!/usr/bin/env python3
"""Seed demo data so dashboard shows non-zero metrics. Run from project root with PYTHONPATH=backend."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.core.database import SessionLocal, init_db
from app.models.workflow import Workflow, WorkflowExecution, ExecutionStep, WorkflowStatus, ExecutionStatus

def seed():
    init_db()
    db = SessionLocal()
    try:
        if db.query(Workflow).count() > 0:
            print("Data already exists, skipping seed.")
            return
        w = Workflow(
            name="Demo Workflow",
            description="Sample workflow for dashboard demo",
            definition={"nodes": [{"id": "1", "type": "http_request", "data": {"label": "API Call"}}], "edges": []},
            status=WorkflowStatus.ACTIVE,
        )
        db.add(w)
        db.commit()
        db.refresh(w)
        for i in range(3):
            exec = WorkflowExecution(
                workflow_id=w.id,
                status=ExecutionStatus.SUCCESS,
                trigger_type="manual",
                duration_seconds=2.5 + i * 0.5,
            )
            db.add(exec)
            db.commit()
            db.refresh(exec)
            step = ExecutionStep(
                execution_id=exec.id,
                step_name="API Call",
                step_type="http_request",
                status=ExecutionStatus.SUCCESS,
                duration_seconds=1.0,
            )
            db.add(step)
        db.commit()
        print("Demo data seeded: 1 workflow, 3 successful executions.")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
