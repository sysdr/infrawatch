import asyncio
import time
from typing import Dict, Any, Callable
import structlog

logger = structlog.get_logger()

class CollectionScheduler:
    def __init__(self):
        self.schedules = {}
        self.running_tasks = {}
        self._running = False

    async def start(self):
        self._running = True
        logger.info("Collection scheduler started")

    async def stop(self):
        self._running = False
        # Cancel all running tasks
        for task in self.running_tasks.values():
            task.cancel()
        self.running_tasks.clear()

    def schedule_collection(self, agent_id: str, metric_type: str, 
                          interval: int, callback: Callable):
        """Schedule metric collection for an agent"""
        schedule_key = f"{agent_id}:{metric_type}"
        
        self.schedules[schedule_key] = {
            "agent_id": agent_id,
            "metric_type": metric_type,
            "interval": interval,
            "callback": callback,
            "last_run": 0,
            "run_count": 0
        }
        
        # Start collection task
        if schedule_key not in self.running_tasks:
            self.running_tasks[schedule_key] = asyncio.create_task(
                self._run_scheduled_collection(schedule_key)
            )
        
        logger.info(f"Scheduled {metric_type} collection for {agent_id} every {interval}s")

    async def _run_scheduled_collection(self, schedule_key: str):
        """Run scheduled collection for a specific agent/metric combination"""
        schedule = self.schedules[schedule_key]
        
        while self._running and schedule_key in self.schedules:
            try:
                current_time = time.time()
                
                # Check if it's time to run
                if (current_time - schedule["last_run"]) >= schedule["interval"]:
                    await schedule["callback"](
                        schedule["agent_id"], 
                        schedule["metric_type"]
                    )
                    
                    schedule["last_run"] = current_time
                    schedule["run_count"] += 1
                    
                    logger.debug(f"Executed scheduled collection: {schedule_key}")
                
                # Sleep for a short interval to avoid busy waiting
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in scheduled collection {schedule_key}: {e}")
                await asyncio.sleep(5)  # Wait before retrying

    def update_schedule(self, agent_id: str, metric_type: str, new_interval: int):
        """Update collection interval for existing schedule"""
        schedule_key = f"{agent_id}:{metric_type}"
        
        if schedule_key in self.schedules:
            self.schedules[schedule_key]["interval"] = new_interval
            logger.info(f"Updated {schedule_key} interval to {new_interval}s")

    def remove_schedule(self, agent_id: str, metric_type: str):
        """Remove scheduled collection"""
        schedule_key = f"{agent_id}:{metric_type}"
        
        if schedule_key in self.schedules:
            del self.schedules[schedule_key]
            
        if schedule_key in self.running_tasks:
            self.running_tasks[schedule_key].cancel()
            del self.running_tasks[schedule_key]
            
        logger.info(f"Removed schedule: {schedule_key}")

    def get_schedules(self) -> Dict[str, Any]:
        """Get current schedules status"""
        return {
            key: {
                "agent_id": schedule["agent_id"],
                "metric_type": schedule["metric_type"],
                "interval": schedule["interval"],
                "run_count": schedule["run_count"],
                "last_run": schedule["last_run"]
            }
            for key, schedule in self.schedules.items()
        }
