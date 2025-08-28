from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from ..aggregation.engine import AggregationEngine
from ..aggregation.rollup import RollupManager
from ..aggregation.statistics import StatisticalCalculator
from ..storage.timeseries import TimeSeriesStorage
from ..models.metrics import MetricData, AggregatedMetric

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize components
aggregation_engine = AggregationEngine()
rollup_manager = RollupManager()
stats_calculator = StatisticalCalculator()
storage = TimeSeriesStorage()

@router.get("/metrics/current")
async def get_current_metrics():
    """Get current real-time aggregated metrics"""
    try:
        aggregations = await aggregation_engine.get_current_aggregations()
        return {
            "status": "success",
            "data": aggregations,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting current metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/summary")
async def get_aggregation_summary():
    """Get aggregation engine summary"""
    try:
        summary = await aggregation_engine.get_aggregation_summary()
        return {
            "status": "success",
            "data": summary,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting aggregation summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/trends/{metric_name}")
async def get_metric_trends(
    metric_name: str,
    lookback_minutes: int = Query(30, description="Lookback period in minutes")
):
    """Get trend analysis for a specific metric"""
    try:
        trends = await aggregation_engine.get_trends(metric_name, lookback_minutes)
        return {
            "status": "success",
            "metric_name": metric_name,
            "lookback_minutes": lookback_minutes,
            "trends": trends,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting trends for {metric_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rollups/status")
async def get_rollup_status():
    """Get rollup manager status"""
    try:
        status = await rollup_manager.get_rollup_status()
        return {
            "status": "success",
            "data": status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting rollup status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rollups/trigger")
async def trigger_rollup():
    """Manually trigger rollup operations"""
    try:
        await rollup_manager.perform_rollups()
        return {
            "status": "success",
            "message": "Rollup operations triggered",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error triggering rollup: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics/calculate")
async def calculate_statistics(
    values: str = Query(..., description="Comma-separated list of values"),
    operation: str = Query("all", description="Statistical operation to perform")
):
    """Calculate statistics for provided values"""
    try:
        # Parse values
        value_list = [float(v.strip()) for v in values.split(",") if v.strip()]
        
        if not value_list:
            raise HTTPException(status_code=400, detail="No valid values provided")
        
        results = {}
        
        if operation == "all" or operation == "percentiles":
            results["percentiles"] = {
                "p50": stats_calculator.percentile(value_list, 50),
                "p95": stats_calculator.percentile(value_list, 95),
                "p99": stats_calculator.percentile(value_list, 99)
            }
        
        if operation == "all" or operation == "basic":
            results["basic"] = {
                "count": len(value_list),
                "sum": sum(value_list),
                "average": sum(value_list) / len(value_list),
                "min": min(value_list),
                "max": max(value_list)
            }
        
        if operation == "all" or operation == "advanced":
            results["advanced"] = {
                "std_dev": stats_calculator.standard_deviation(value_list),
                "variance": stats_calculator.variance(value_list),
                "rate_of_change": stats_calculator.rate_of_change(value_list)
            }
        
        if operation == "all" or operation == "anomalies":
            anomalies = stats_calculator.detect_anomalies(value_list)
            results["anomalies"] = {
                "indices": anomalies,
                "count": len(anomalies),
                "values": [value_list[i] for i in anomalies]
            }
        
        return {
            "status": "success",
            "operation": operation,
            "input_count": len(value_list),
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid values format: {e}")
    except Exception as e:
        logger.error(f"Error calculating statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "components": {
            "aggregation_engine": "running",
            "rollup_manager": "running",
            "statistics_calculator": "running",
            "storage": "connected"
        },
        "timestamp": datetime.utcnow().isoformat()
    }
