from sqlalchemy import Column, Integer, String, DateTime, Text, Index, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import TSVECTOR
from datetime import datetime

Base = declarative_base()

class Log(Base):
    __tablename__ = "logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    level = Column(String(20), index=True)
    service = Column(String(100), index=True)
    message = Column(Text)
    user_id = Column(String(50), index=True, nullable=True)
    request_id = Column(String(100), index=True, nullable=True)
    # renamed from 'metadata' because SQLAlchemy reserves that name on declarative models
    metadata_json = Column("metadata", Text, nullable=True)
    search_vector = Column(TSVECTOR)
    
    __table_args__ = (
        Index('idx_logs_composite', 'service', 'level', 'timestamp'),
        Index('idx_logs_search', 'search_vector', postgresql_using='gin'),
        Index('idx_logs_message_trgm', 'message', postgresql_using='gin', postgresql_ops={'message': 'gin_trgm_ops'}),
        Index('idx_error_logs', 'timestamp', postgresql_where=text("level = 'error'")),
    )

class SearchQuery(Base):
    __tablename__ = "search_queries"
    
    id = Column(Integer, primary_key=True, index=True)
    query_string = Column(Text)
    user_id = Column(String(50), index=True)
    execution_time_ms = Column(Integer)
    result_count = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    cache_hit = Column(String(10))
