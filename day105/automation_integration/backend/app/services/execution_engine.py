import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import json

from app.core.database import AsyncSessionLocal
from app.models.workflow import (
    WorkflowExecution, ExecutionStep, ExecutionLog,
    ExecutionStatus, StepStatus, Workflow
)
from app.services.security_validator import security_validator
from app.services.error_recovery import error_recovery
from app.services.websocket_manager import ws_manager

logger = logging.getLogger(__name__)

class ExecutionEngine:
    """Production workflow execution engine with security validation and error recovery"""
    
    def __init__(self):
        self.running = False
        self.execution_queue = asyncio.Queue()
        self.active_executions: Dict[int, asyncio.Task] = {}
        self.max_concurrent = 10
        self.worker_tasks: List[asyncio.Task] = []
        
    async def start(self):
        """Start the execution engine workers"""
        self.running = True
        logger.info(f"Starting execution engine with {self.max_concurrent} workers")
        
        # Start worker tasks
        for i in range(self.max_concurrent):
            task = asyncio.create_task(self._worker(i))
            self.worker_tasks.append(task)
    
    async def stop(self):
        """Stop the execution engine gracefully"""
        self.running = False
        logger.info("Stopping execution engine...")
        
        # Cancel all worker tasks
        for task in self.worker_tasks:
            task.cancel()
        
        # Wait for all tasks to complete
        await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        
        # Cancel active executions
        for task in self.active_executions.values():
            task.cancel()
        
        logger.info("Execution engine stopped")
    
    async def submit_execution(self, execution_id: int):
        """Submit a workflow execution to the queue"""
        await self.execution_queue.put(execution_id)
        logger.info(f"Execution {execution_id} submitted to queue")
    
    async def _worker(self, worker_id: int):
        """Worker coroutine that processes executions from the queue"""
        logger.info(f"Worker {worker_id} started")
        
        while self.running:
            try:
                # Get execution from queue with timeout
                execution_id = await asyncio.wait_for(
                    self.execution_queue.get(),
                    timeout=1.0
                )
                
                # Execute the workflow
                task = asyncio.create_task(self._execute_workflow(execution_id))
                self.active_executions[execution_id] = task
                
                try:
                    await task
                except Exception as e:
                    logger.error(f"Worker {worker_id} execution {execution_id} failed: {e}")
                finally:
                    self.active_executions.pop(execution_id, None)
                    
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
    
    async def _execute_workflow(self, execution_id: int):
        """Execute a workflow with security validation and error recovery"""
        async with AsyncSessionLocal() as session:
            try:
                # Load execution
                result = await session.execute(
                    select(WorkflowExecution).where(WorkflowExecution.id == execution_id)
                )
                execution = result.scalar_one_or_none()
                
                if not execution:
                    logger.error(f"Execution {execution_id} not found")
                    return
                
                # Load workflow definition
                result = await session.execute(
                    select(Workflow).where(Workflow.id == execution.workflow_id)
                )
                workflow = result.scalar_one_or_none()
                
                if not workflow:
                    logger.error(f"Workflow {execution.workflow_id} not found")
                    return
                
                # Update status to running
                execution.status = ExecutionStatus.RUNNING
                execution.started_at = datetime.utcnow()
                await session.commit()
                
                # Broadcast status update
                await ws_manager.broadcast_execution_update(execution_id, {
                    "status": "running",
                    "started_at": execution.started_at.isoformat()
                })
                
                # Log start
                await self._log_execution(session, execution_id, "INFO", 
                                         f"Starting workflow execution: {workflow.name}")
                
                # Security validation
                security_passed = await security_validator.validate_execution(
                    session, execution_id, execution.input_data
                )
                
                if not security_passed:
                    raise Exception("Security validation failed")
                
                # Execute workflow steps
                steps_definition = workflow.definition.get("steps", [])
                context = {"input": execution.input_data, "outputs": {}}
                
                for step_def in steps_definition:
                    step = await self._execute_step(
                        session, execution_id, step_def, context
                    )
                    
                    if step.status == StepStatus.FAILED:
                        # Attempt error recovery
                        recovered = await error_recovery.attempt_recovery(
                            session, execution_id, step.id, step.error_message
                        )
                        
                        if not recovered:
                            raise Exception(f"Step {step.step_name} failed: {step.error_message}")
                    
                    # Store step output in context
                    context["outputs"][step.step_name] = step.output_data
                
                # Mark execution as completed
                execution.status = ExecutionStatus.COMPLETED
                execution.completed_at = datetime.utcnow()
                execution.execution_time = (
                    execution.completed_at - execution.started_at
                ).total_seconds()
                execution.output_data = context["outputs"]
                
                await session.commit()
                
                # Broadcast completion
                await ws_manager.broadcast_execution_update(execution_id, {
                    "status": "completed",
                    "completed_at": execution.completed_at.isoformat(),
                    "execution_time": execution.execution_time
                })
                
                await self._log_execution(session, execution_id, "INFO",
                                         f"Workflow completed in {execution.execution_time:.2f}s")
                
            except Exception as e:
                logger.error(f"Execution {execution_id} failed: {e}")
                
                # Update execution status
                execution.status = ExecutionStatus.FAILED
                execution.error_message = str(e)
                execution.completed_at = datetime.utcnow()
                if execution.started_at:
                    execution.execution_time = (
                        execution.completed_at - execution.started_at
                    ).total_seconds()
                
                await session.commit()
                
                # Broadcast failure
                await ws_manager.broadcast_execution_update(execution_id, {
                    "status": "failed",
                    "error_message": str(e)
                })
                
                await self._log_execution(session, execution_id, "ERROR", str(e))
    
    async def _execute_step(
        self, 
        session: AsyncSession,
        execution_id: int,
        step_def: Dict,
        context: Dict
    ) -> ExecutionStep:
        """Execute a single workflow step"""
        step_name = step_def.get("name")
        step_type = step_def.get("type")
        
        # Create step record
        step = ExecutionStep(
            execution_id=execution_id,
            step_name=step_name,
            step_type=step_type,
            status=StepStatus.RUNNING,
            started_at=datetime.utcnow(),
            input_data=step_def.get("input", {})
        )
        session.add(step)
        await session.commit()
        await session.refresh(step)
        
        await self._log_execution(session, execution_id, "INFO",
                                 f"Starting step: {step_name}", step_name)
        
        try:
            # Execute step based on type
            if step_type == "script":
                output = await self._execute_script_step(step_def, context)
            elif step_type == "api":
                output = await self._execute_api_step(step_def, context)
            elif step_type == "transform":
                output = await self._execute_transform_step(step_def, context)
            else:
                # Generic execution
                output = {"result": "success", "data": step_def.get("output", {})}
            
            # Update step as completed
            step.status = StepStatus.COMPLETED
            step.completed_at = datetime.utcnow()
            step.execution_time = (step.completed_at - step.started_at).total_seconds()
            step.output_data = output
            
            await session.commit()
            
            await self._log_execution(session, execution_id, "INFO",
                                     f"Step completed: {step_name} in {step.execution_time:.2f}s",
                                     step_name)
            
        except Exception as e:
            logger.error(f"Step {step_name} failed: {e}")
            step.status = StepStatus.FAILED
            step.error_message = str(e)
            step.completed_at = datetime.utcnow()
            step.execution_time = (step.completed_at - step.started_at).total_seconds()
            
            await session.commit()
            
            await self._log_execution(session, execution_id, "ERROR",
                                     f"Step failed: {step_name} - {str(e)}", step_name)
        
        return step
    
    async def _execute_script_step(self, step_def: Dict, context: Dict) -> Dict:
        """Execute a script step (simulated)"""
        await asyncio.sleep(0.5)  # Simulate execution
        return {
            "result": "success",
            "output": f"Script executed: {step_def.get('script', '')}"
        }
    
    async def _execute_api_step(self, step_def: Dict, context: Dict) -> Dict:
        """Execute an API call step (simulated)"""
        await asyncio.sleep(0.3)  # Simulate API call
        return {
            "result": "success",
            "response": {
                "status": 200,
                "data": {"message": "API call successful"}
            }
        }
    
    async def _execute_transform_step(self, step_def: Dict, context: Dict) -> Dict:
        """Execute a data transformation step"""
        transform_func = step_def.get("function", "identity")
        input_data = context.get("outputs", {}).get(step_def.get("input_step", ""), {})
        
        # Simple transformation
        await asyncio.sleep(0.2)
        return {
            "result": "success",
            "transformed_data": input_data
        }
    
    async def _log_execution(
        self,
        session: AsyncSession,
        execution_id: int,
        level: str,
        message: str,
        step_name: Optional[str] = None
    ):
        """Log execution event"""
        log = ExecutionLog(
            execution_id=execution_id,
            level=level,
            message=message,
            step_name=step_name,
            timestamp=datetime.utcnow()
        )
        session.add(log)
        await session.commit()

# Global execution engine instance
execution_engine = ExecutionEngine()
