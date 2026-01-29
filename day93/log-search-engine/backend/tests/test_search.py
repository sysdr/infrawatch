import pytest
from app.services.query_parser import parser
from app.services.sql_translator import sql_translator
from sqlalchemy import select
from app.models.log import Log

def test_query_parser_field():
    """Test parsing field queries"""
    ast = parser.parse("level:error")
    assert ast["type"] == "field"
    assert ast["field"] == "level"
    assert ast["value"] == "error"

def test_query_parser_range():
    """Test parsing range queries"""
    ast = parser.parse("timestamp:[2025-01-01 TO 2025-01-31]")
    assert ast["type"] == "range"
    assert ast["field"] == "timestamp"

def test_query_parser_wildcard():
    """Test parsing wildcard queries"""
    ast = parser.parse("service:api-*")
    assert ast["type"] == "wildcard"
    assert ast["field"] == "service"

def test_query_parser_boolean():
    """Test parsing boolean queries"""
    ast = parser.parse("level:error AND service:api")
    assert ast["type"] == "and"
    assert ast["left"]["field"] == "level"
    assert ast["right"]["field"] == "service"

def test_sql_translator():
    """Test SQL translation"""
    ast = {"type": "field", "field": "level", "op": ":", "value": "error"}
    query = select(Log)
    result_query, params = sql_translator.translate(ast, query)
    assert result_query is not None
    assert "error" in params

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
