import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models.kpi import KPIMetric, KPIValue
import numpy as np

class DataSeeder:
    def __init__(self, db: Session):
        self.db = db

    def seed_metrics(self):
        metrics = [
            {"name": "revenue", "display_name": "Revenue", "description": "Total revenue", "category": "financial", "unit": "USD", "calculation_method": "sum", "target_value": 100000.0, "critical_threshold": 80000.0, "warning_threshold": 90000.0},
            {"name": "user_signups", "display_name": "User Signups", "description": "New user registrations", "category": "growth", "unit": "count", "calculation_method": "count", "target_value": 1000.0, "critical_threshold": 500.0, "warning_threshold": 750.0},
            {"name": "churn_rate", "display_name": "Churn Rate", "description": "User churn percentage", "category": "retention", "unit": "%", "calculation_method": "percentage", "target_value": 5.0, "critical_threshold": 10.0, "warning_threshold": 7.5},
            {"name": "api_latency", "display_name": "API Latency", "description": "Average API response time", "category": "performance", "unit": "ms", "calculation_method": "average", "target_value": 100.0, "critical_threshold": 500.0, "warning_threshold": 300.0},
            {"name": "error_rate", "display_name": "Error Rate", "description": "API error percentage", "category": "reliability", "unit": "%", "calculation_method": "percentage", "target_value": 0.1, "critical_threshold": 1.0, "warning_threshold": 0.5}
        ]
        for m in metrics:
            if not self.db.query(KPIMetric).filter(KPIMetric.name == m["name"]).first():
                self.db.add(KPIMetric(**m))
        self.db.commit()
        print("Sample metrics created")

    def seed_values(self, days: int = 90):
        metrics = self.db.query(KPIMetric).all()
        end_date = datetime.utcnow()
        for metric in metrics:
            for day in range(days):
                timestamp = end_date - timedelta(days=days - day)
                trend = (day / days) * metric.target_value * 0.2
                seasonality = np.sin(2 * np.pi * day / 7) * metric.target_value * 0.1
                noise = random.gauss(0, metric.target_value * 0.05)
                value = max(0, metric.target_value + trend + seasonality + noise)
                if random.random() < 0.05:
                    value *= random.choice([0.7, 1.3])
                dimensions = {}
                if metric.category in ["financial", "growth"]:
                    dimensions["product"] = random.choice(["basic", "premium", "enterprise"])
                    dimensions["region"] = random.choice(["us-east", "us-west", "eu", "asia"])
                self.db.add(KPIValue(metric_id=metric.id, timestamp=timestamp, value=value, dimensions=dimensions if dimensions else None))
            self.db.commit()
        print(f"Generated {days} days of data for {len(metrics)} metrics")
