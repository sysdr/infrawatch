from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
import uvicorn

from services.database import get_db, init_db
from services.kpi_calculator import KPICalculator
from services.trend_analyzer import TrendAnalyzer
from services.forecaster import Forecaster
from services.report_generator import ReportGenerator
from services.comparator import MetricComparator
from services.seeder import DataSeeder
from models.kpi import KPIMetric

app = FastAPI(title="BI Dashboard API", description="Business Intelligence Dashboard", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000", "http://localhost:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
async def startup_event():
    init_db()
    print("Database initialized")

@app.get("/")
async def root():
    return {"message": "BI Dashboard API", "version": "1.0.0", "endpoints": {"kpis": "/api/kpis", "trends": "/api/trends/{metric_name}", "forecast": "/api/forecast/{metric_name}", "compare": "/api/compare", "reports": "/api/reports"}}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/api/kpis")
async def get_kpis(db: Session = Depends(get_db)):
    return {"kpis": KPICalculator(db).get_dashboard_kpis(), "timestamp": datetime.utcnow().isoformat()}

@app.get("/api/kpis/{metric_name}")
async def get_kpi_detail(metric_name: str, days: int = Query(7, ge=1, le=365), db: Session = Depends(get_db)):
    calculator = KPICalculator(db)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    kpi = calculator.calculate_kpi(metric_name, start_date, end_date)
    sparkline = calculator.get_sparkline_data(metric_name, days)
    return {"kpi": kpi, "sparkline": sparkline}

@app.get("/api/trends/{metric_name}")
async def get_trend_analysis(metric_name: str, window_days: int = Query(30, ge=7, le=365), db: Session = Depends(get_db)):
    try:
        return TrendAnalyzer(db).analyze_trend(metric_name, window_days)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend analysis error: {str(e)}")

@app.get("/api/anomalies/{metric_name}")
async def get_anomalies(metric_name: str, threshold: float = Query(2.5, ge=1.0, le=5.0), db: Session = Depends(get_db)):
    try:
        return {"anomalies": TrendAnalyzer(db).detect_anomalies(metric_name, threshold)}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/forecast/{metric_name}")
async def get_forecast(metric_name: str, days: int = Query(7, ge=1, le=30), model: str = Query("arima", regex="^(arima|exponential_smoothing)$"), db: Session = Depends(get_db)):
    try:
        return Forecaster(db).forecast_metric(metric_name, days, model)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/compare/dimension")
async def compare_by_dimension(metric_name: str = Query(...), dimension: str = Query(...), period_days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)):
    try:
        return MetricComparator(db).compare_by_dimension(metric_name, dimension, period_days)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison error: {str(e)}")

@app.get("/api/compare/periods")
async def compare_periods(metric_name: str = Query(...), period1_days: int = Query(7, ge=1), period2_days: int = Query(7, ge=1), db: Session = Depends(get_db)):
    end_date = datetime.utcnow()
    period2_end, period2_start = end_date, end_date - timedelta(days=period2_days)
    period1_end, period1_start = period2_start, period2_start - timedelta(days=period1_days)
    try:
        return MetricComparator(db).compare_time_periods(metric_name, period1_start, period1_end, period2_start, period2_end)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison error: {str(e)}")

@app.post("/api/reports/generate")
async def generate_report(report_type: str = Query("weekly", regex="^(daily|weekly|monthly)$"), db: Session = Depends(get_db)):
    return ReportGenerator(db).generate_executive_report(report_type)

@app.get("/api/metrics")
async def list_metrics(db: Session = Depends(get_db)):
    metrics = db.query(KPIMetric).all()
    return {"metrics": [{"name": m.name, "display_name": m.display_name, "category": m.category, "unit": m.unit} for m in metrics]}

@app.post("/api/seed")
async def seed_data(days: int = Query(90, ge=7, le=365), db: Session = Depends(get_db)):
    seeder = DataSeeder(db)
    seeder.seed_metrics()
    seeder.seed_values(days)
    return {"status": "success", "message": f"Seeded {days} days of data"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
