from app.services.scheduler_service import SchedulerService
from app.database import init_db
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting scheduler service...")
    init_db()
    
    scheduler = SchedulerService()
    scheduler.start()
    
    logger.info("Scheduler running. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping scheduler...")
        scheduler.stop()
