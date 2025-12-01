import asyncio
from datetime import datetime, timedelta
from database.db_config import AsyncSessionLocal
from services.aggregator import AggregationService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_hourly_aggregation():
    """Run hourly aggregation job"""
    while True:
        try:
            # Aggregate previous hour
            current_hour = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
            previous_hour = current_hour - timedelta(hours=1)
            
            async with AsyncSessionLocal() as db:
                aggregator = AggregationService(db)
                await aggregator.aggregate_hourly_metrics(previous_hour)
                logger.info(f"Completed hourly aggregation for {previous_hour}")
            
            # Wait for next hour
            await asyncio.sleep(3600)
            
        except Exception as e:
            logger.error(f"Error in hourly aggregation: {e}")
            await asyncio.sleep(60)

async def run_daily_aggregation():
    """Run daily aggregation job"""
    while True:
        try:
            # Aggregate previous day
            current_day = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            previous_day = current_day - timedelta(days=1)
            
            async with AsyncSessionLocal() as db:
                aggregator = AggregationService(db)
                await aggregator.aggregate_daily_metrics(previous_day)
                logger.info(f"Completed daily aggregation for {previous_day}")
            
            # Wait for next day
            await asyncio.sleep(86400)
            
        except Exception as e:
            logger.error(f"Error in daily aggregation: {e}")
            await asyncio.sleep(3600)

def start_aggregation_jobs():
    """Start all aggregation background jobs"""
    loop = asyncio.get_event_loop()
    loop.create_task(run_hourly_aggregation())
    loop.create_task(run_daily_aggregation())
    logger.info("Started aggregation background jobs")
