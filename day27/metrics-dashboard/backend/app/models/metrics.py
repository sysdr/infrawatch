from sqlalchemy import Column, Integer, Float, String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

Base = declarative_base()

class MetricData(Base):
    __tablename__ = "metric_data"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String, index=True)
    value = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    labels = Column(String)  # JSON string for labels
    
    def to_dict(self):
        return {
            "id": self.id,
            "metric_name": self.metric_name,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "labels": json.loads(self.labels) if self.labels else {}
        }

# Database setup
engine = create_engine("sqlite:///./metrics.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
