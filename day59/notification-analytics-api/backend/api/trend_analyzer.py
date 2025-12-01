from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from database.db_config import get_db
from services.aggregator import AggregationService
from services.trend_analyzer import TrendAnalyzer
from pydantic import BaseModel

router = APIRouter(prefix="/api/analytics", tags=["trends"])

class TrendAnalysisResponse(BaseModel):
    metric: str
    time_range: str
    current_value: float
    percent_change: float
    direction: str
    trend: str
    anomalies: list
    moving_average: list

@router.get("/trends")
async def analyze_trends(
    metric: str = Query(..., description="Metric to analyze"),
    channel: Optional[str] = Query(None, description="Filter by channel"),
    days: int = Query(7, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """Analyze trends in metric data"""
    
    end = datetime.utcnow()
    start = end - timedelta(days=days)
    
    # Query data
    aggregator = AggregationService(db)
    filters = {'channel': channel} if channel else None
    
    data = await aggregator.query_metrics(
        metric=metric,
        group_by=['time'],
        start=start,
        end=end,
        filters=filters
    )
    
    if not data:
        return TrendAnalysisResponse(
            metric=metric,
            time_range=f"{start} to {end}",
            current_value=0,
            percent_change=0,
            direction="stable",
            trend="stable",
            anomalies=[],
            moving_average=[]
        )
    
    # Perform trend analysis
    analyzer = TrendAnalyzer()
    analysis = analyzer.analyze_trends(data, window=min(7, len(data)))
    
    return TrendAnalysisResponse(
        metric=metric,
        time_range=f"{start} to {end}",
        current_value=data[-1]['value'] if data else 0,
        percent_change=analysis.percent_change,
        direction=analysis.direction,
        trend=analysis.trend,
        anomalies=analysis.anomalies,
        moving_average=analysis.moving_average
    )

@router.get("/anomalies")
async def detect_anomalies(
    metric: str,
    channel: Optional[str] = None,
    hours: int = Query(24, description="Time window to check"),
    threshold: float = Query(2.0, description="Standard deviations for anomaly"),
    db: AsyncSession = Depends(get_db)
):
    """Detect anomalies in recent metrics"""
    
    end = datetime.utcnow()
    start = end - timedelta(hours=hours)
    
    aggregator = AggregationService(db)
    filters = {'channel': channel} if channel else None
    
    data = await aggregator.query_metrics(
        metric=metric,
        group_by=['time'],
        start=start,
        end=end,
        filters=filters
    )
    
    analyzer = TrendAnalyzer()
    anomalies = analyzer.detect_anomalies(data, threshold)
    
    return {
        "metric": metric,
        "time_range": f"{start} to {end}",
        "total_points": len(data),
        "anomalies_detected": len(anomalies),
        "anomalies": anomalies
    }
