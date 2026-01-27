"""Monitoring service"""
import structlog

logger = structlog.get_logger()

class MonitoringService:
    def __init__(self):
        self.active = True
        logger.info("monitoring_service_initialized")
