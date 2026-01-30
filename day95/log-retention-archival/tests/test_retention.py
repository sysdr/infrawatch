import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Base
from models.log_entry import LogEntry, RetentionPolicy, StorageTier
from services.retention_service import RetentionService
from datetime import datetime, timedelta

@pytest.fixture
def db_session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_retention_policy_evaluation(db_session):
    # Create policy
    policy = RetentionPolicy(
        name="Test Policy",
        log_source_pattern="test.*",
        hot_retention_days=7,
        warm_retention_days=30,
        cold_retention_days=90
    )
    db_session.add(policy)
    db_session.commit()
    
    # Create old log
    old_log = LogEntry(
        id="test-1",
        source="test-source",
        level="info",
        message="Test message",
        timestamp=datetime.utcnow() - timedelta(days=10),
        storage_tier=StorageTier.HOT
    )
    db_session.add(old_log)
    db_session.commit()
    
    # Evaluate
    service = RetentionService(db_session)
    transitions = service.evaluate_retention_policies()
    
    assert len(transitions) > 0
    assert transitions[0]["target_tier"] == StorageTier.WARM

def test_cost_calculation():
    from services.cost_service import CostService
    
    assert CostService.TIER_COSTS[StorageTier.HOT] == 0.023
    assert CostService.TIER_COSTS[StorageTier.WARM] == 0.004
    assert CostService.TIER_COSTS[StorageTier.COLD] == 0.001

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
