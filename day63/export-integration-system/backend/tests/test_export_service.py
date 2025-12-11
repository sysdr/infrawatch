import pytest
import tempfile
import os
from app.services.export_service import StreamingExporter
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Create test table
    session.execute(text("""
        CREATE TABLE metrics (
            id TEXT PRIMARY KEY,
            metric_name TEXT,
            value REAL,
            timestamp TEXT,
            tags TEXT
        )
    """))
    
    # Insert test data
    for i in range(1000):
        session.execute(text("""
            INSERT INTO metrics VALUES (:id, :name, :value, :ts, :tags)
        """), {
            'id': f'test-{i}',
            'name': f'metric_{i % 10}',
            'value': float(i),
            'ts': '2025-01-01',
            'tags': '{}'
        })
    session.commit()
    
    yield session
    session.close()

def test_csv_export(db_session):
    exporter = StreamingExporter(db_session)
    query = db_session.execute(text("SELECT * FROM metrics"))
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        output_path = f.name
    
    try:
        result = exporter.export_to_csv(query, output_path)
        
        assert result['row_count'] == 1000
        assert result['file_size'] > 0
        assert os.path.exists(output_path)
        
        # Verify file contents
        with open(output_path, 'r') as f:
            lines = f.readlines()
            assert len(lines) == 1001  # Header + 1000 rows
    finally:
        os.unlink(output_path)

def test_json_export(db_session):
    exporter = StreamingExporter(db_session)
    query = db_session.execute(text("SELECT * FROM metrics LIMIT 10"))
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        output_path = f.name
    
    try:
        result = exporter.export_to_json(query, output_path)
        
        assert result['row_count'] == 10
        assert os.path.exists(output_path)
        
        import json
        with open(output_path, 'r') as f:
            data = json.load(f)
            assert len(data) == 10
    finally:
        os.unlink(output_path)

def test_export_validation(db_session):
    exporter = StreamingExporter(db_session)
    query = db_session.execute(text("SELECT * FROM metrics LIMIT 100"))
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        output_path = f.name
    
    try:
        result = exporter.export_to_csv(query, output_path)
        checksum = result['checksum']
        
        # Validation should pass
        is_valid = exporter.validate_export(output_path, 'csv', checksum)
        assert is_valid is True
        
        # Validation with wrong checksum should fail
        is_valid = exporter.validate_export(output_path, 'csv', 'wrong_checksum')
        assert is_valid is False
    finally:
        os.unlink(output_path)

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
