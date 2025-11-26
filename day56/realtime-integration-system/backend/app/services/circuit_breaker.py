import asyncio
from datetime import datetime, timedelta
from typing import Callable, Any
import structlog

logger = structlog.get_logger()

class CircuitBreaker:
    """Circuit breaker pattern implementation"""
    
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"
    
    def __init__(self, name: str, failure_threshold: int = 5, 
                 recovery_timeout: int = 30, success_threshold: int = 2):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        
        self.state = self.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state_change_time = datetime.now()
    
    def is_open(self) -> bool:
        """Check if circuit breaker is open"""
        if self.state == self.OPEN:
            # Check if recovery timeout elapsed
            if datetime.now() - self.state_change_time > timedelta(seconds=self.recovery_timeout):
                self._transition_to_half_open()
            return True
        return False
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        if self.is_open():
            raise Exception(f"Circuit breaker {self.name} is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            raise e
    
    def record_success(self):
        """Record successful call"""
        self.failure_count = 0
        
        if self.state == self.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self._transition_to_closed()
    
    def record_failure(self):
        """Record failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.state == self.HALF_OPEN:
            self._transition_to_open()
        elif self.failure_count >= self.failure_threshold:
            self._transition_to_open()
    
    def _transition_to_closed(self):
        """Transition to CLOSED state"""
        self.state = self.CLOSED
        self.success_count = 0
        self.failure_count = 0
        self.state_change_time = datetime.now()
        logger.info("Circuit breaker closed", name=self.name)
    
    def _transition_to_open(self):
        """Transition to OPEN state"""
        self.state = self.OPEN
        self.state_change_time = datetime.now()
        logger.warning("Circuit breaker opened", name=self.name)
    
    def _transition_to_half_open(self):
        """Transition to HALF_OPEN state"""
        self.state = self.HALF_OPEN
        self.success_count = 0
        self.state_change_time = datetime.now()
        logger.info("Circuit breaker half-open", name=self.name)
    
    def get_state(self) -> str:
        """Get current state"""
        return self.state
