from croniter import croniter
from datetime import datetime, timedelta
from typing import Optional
import pytz

class CronScheduler:
    """Handle cron-based scheduling"""
    
    def parse_cron(self, cron_expression: str, timezone: str = "UTC") -> datetime:
        """Parse cron expression and return next run time"""
        
        tz = pytz.timezone(timezone)
        base_time = datetime.now(tz)
        
        try:
            cron = croniter(cron_expression, base_time)
            next_run = cron.get_next(datetime)
            return next_run
        except Exception as e:
            raise ValueError(f"Invalid cron expression: {cron_expression}")
    
    def should_execute(self, cron_expression: str, last_run: Optional[datetime], timezone: str = "UTC") -> bool:
        """Check if schedule should execute now"""
        
        if last_run is None:
            return True
        
        tz = pytz.timezone(timezone)
        now = datetime.now(tz)
        
        cron = croniter(cron_expression, last_run.astimezone(tz))
        next_run = cron.get_next(datetime)
        
        return now >= next_run
    
    def add_jitter(self, schedule_time: datetime, max_jitter_minutes: int = 5) -> datetime:
        """Add random jitter to prevent thundering herd"""
        
        import random
        jitter_seconds = random.randint(0, max_jitter_minutes * 60)
        return schedule_time + timedelta(seconds=jitter_seconds)
