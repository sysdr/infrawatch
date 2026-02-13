import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.kpi import Base, KPIMetric, KPIValue
from services.kpi_calculator import KPICalculator

@pytest.fixture
def db_session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    metric = KPIMetric(name="test_metric", display_name="Test Metric", category="test", unit="count", calculation_method="sum", target_value=100.0)
    session.add(metric)
    session.commit()
    for i in range(14):
        session.add(KPIValue(metric_id=metric.id, timestamp=datetime.utcnow() - timedelta(days=14-i), value=50.0 + i * 2))
    session.commit()
    yield session
    session.close()

def test_calculate_kpi(db_session):
    calculator = KPICalculator(db_session)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)
    result = calculator.calculate_kpi("test_metric", start_date, end_date)
    assert result["metric_name"] == "test_metric"
    assert result["current_value"] is not None
    assert result["trend"] in ["up", "down", "stable", "unknown"]

def test_get_dashboard_kpis(db_session):
    calculator = KPICalculator(db_session)
    kpis = calculator.get_dashboard_kpis()
    assert len(kpis) > 0
    assert all("metric_name" in kpi for kpi in kpis)
