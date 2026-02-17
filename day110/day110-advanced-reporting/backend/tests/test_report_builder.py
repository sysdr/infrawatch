import pytest
from app.services.builders.report_builder import ReportBuilder
import pandas as pd

def test_execute_query():
    builder = ReportBuilder()
    query_config = {
        "metrics": ["cpu_usage", "memory_usage"],
        "aggregations": {"cpu_usage": "mean"}
    }
    parameters = {"time_range": "7d"}
    
    df = builder.execute_query(query_config, parameters)
    
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "cpu_usage" in df.columns

def test_query_with_aggregations():
    builder = ReportBuilder()
    query_config = {
        "metrics": ["cpu_usage"],
        "aggregations": {"cpu_usage": "max"}
    }
    parameters = {"time_range": "1d"}
    
    df = builder.execute_query(query_config, parameters)
    assert "cpu_usage" in df.columns
