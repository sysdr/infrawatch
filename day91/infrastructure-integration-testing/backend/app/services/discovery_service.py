"""Resource discovery service"""
import structlog

logger = structlog.get_logger()

class DiscoveryService:
    def __init__(self):
        self.active = True
        logger.info("discovery_service_initialized")
