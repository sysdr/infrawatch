import asyncio
import json
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, asdict
import uuid

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    READY = "ready" 
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class RetryStrategy(Enum):
    IMMEDIATE = "immediate"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    CIRCUIT_BREAKER = "circuit_breaker"

@dataclass
class Task:
    id: str
    name: str
    function: str
    params: Dict[str, Any]
    depends_on: List[str]
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: str = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    retry_strategy: RetryStrategy = RetryStrategy.IMMEDIATE
    condition: Optional[str] = None
    callbacks: Dict[str, List[str]] = None

    def __post_init__(self):
        if self.callbacks is None:
            self.callbacks = {
                'on_start': [],
                'on_success': [], 
                'on_failure': [],
                'on_completion': []
            }

@dataclass
class Workflow:
    id: str
    name: str
    tasks: List[Task]
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    context: Dict[str, Any] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.context is None:
            self.context = {}

class WorkflowEngine:
    def __init__(self, task_manager):
        self.task_manager = task_manager
        self.workflows: Dict[str, Workflow] = {}
        self.running = False
        self.task_functions: Dict[str, Callable] = {}
        self.callback_functions: Dict[str, Callable] = {}
        self._register_builtin_functions()
        
    def _register_builtin_functions(self):
        """Register built-in task functions"""
        self.task_functions = {
            'process_payment': self._process_payment,
            'reserve_inventory': self._reserve_inventory,
            'create_shipping_label': self._create_shipping_label,
            'send_notification': self._send_notification,
            'validate_content': self._validate_content,
            'detect_spam': self._detect_spam,
            'manual_review': self._manual_review,
            'publish_content': self._publish_content,
            'invalidate_cache': self._invalidate_cache,
            'post_to_social': self._post_to_social,
        }
        
        self.callback_functions = {
            'log_start': self._log_start,
            'log_success': self._log_success,
            'log_failure': self._log_failure,
            'send_alert': self._send_alert,
        }

    async def create_workflow(self, workflow_def: Dict) -> str:
        """Create a new workflow from definition"""
        workflow_id = str(uuid.uuid4())
        
        tasks = []
        for task_def in workflow_def['tasks']:
            task = Task(
                id=task_def['id'],
                name=task_def['name'],
                function=task_def['function'],
                params=task_def.get('params', {}),
                depends_on=task_def.get('depends_on', []),
                condition=task_def.get('condition'),
                max_retries=task_def.get('max_retries', 3),
                retry_strategy=RetryStrategy(task_def.get('retry_strategy', 'immediate')),
                callbacks=task_def.get('callbacks', {})
            )
            tasks.append(task)
        
        workflow = Workflow(
            id=workflow_id,
            name=workflow_def['name'],
            tasks=tasks,
            context=workflow_def.get('context', {})
        )
        
        # Validate workflow (check for cycles, etc.)
        if not self._validate_workflow(workflow):
            raise ValueError("Invalid workflow: contains cycles or invalid dependencies")
        
        self.workflows[workflow_id] = workflow
        return workflow_id

    def _validate_workflow(self, workflow: Workflow) -> bool:
        """Validate workflow for cycles and dependency consistency"""
        task_ids = {task.id for task in workflow.tasks}
        
        # Check all dependencies exist
        for task in workflow.tasks:
            for dep in task.depends_on:
                if dep not in task_ids:
                    return False
        
        # Check for cycles using DFS
        def has_cycle(task_id: str, visited: set, rec_stack: set) -> bool:
            visited.add(task_id)
            rec_stack.add(task_id)
            
            task = next(t for t in workflow.tasks if t.id == task_id)
            for dep in task.depends_on:
                if dep not in visited:
                    if has_cycle(dep, visited, rec_stack):
                        return True
                elif dep in rec_stack:
                    return True
            
            rec_stack.remove(task_id)
            return False
        
        visited = set()
        for task in workflow.tasks:
            if task.id not in visited:
                if has_cycle(task.id, visited, set()):
                    return True
        
        return True

    async def execute_workflow(self, workflow_id: str):
        """Execute a workflow with dependency resolution"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow.status = TaskStatus.RUNNING
        workflow.started_at = datetime.now()
        
        logger.info(f"Starting workflow execution: {workflow.name}")
        
        try:
            while not self._workflow_complete(workflow):
                ready_tasks = self._get_ready_tasks(workflow)
                
                if not ready_tasks:
                    # Check if we're stuck
                    if self._has_pending_tasks(workflow):
                        logger.error("Workflow stuck - no ready tasks but pending tasks exist")
                        break
                    else:
                        break
                
                # Execute ready tasks concurrently
                tasks_to_execute = []
                for task in ready_tasks:
                    if self._should_execute_task(task, workflow):
                        tasks_to_execute.append(self._execute_task(task, workflow))
                
                if tasks_to_execute:
                    await asyncio.gather(*tasks_to_execute, return_exceptions=True)
                
                # Small delay to prevent tight loop
                await asyncio.sleep(0.1)
        
        except Exception as e:
            workflow.status = TaskStatus.FAILED
            logger.error(f"Workflow execution failed: {str(e)}")
        
        workflow.completed_at = datetime.now()
        if workflow.status == TaskStatus.RUNNING:
            workflow.status = TaskStatus.COMPLETED
        
        logger.info(f"Workflow completed: {workflow.name} - {workflow.status.value}")

    def _get_ready_tasks(self, workflow: Workflow) -> List[Task]:
        """Get tasks that are ready to execute"""
        ready_tasks = []
        
        for task in workflow.tasks:
            if task.status != TaskStatus.PENDING:
                continue
            
            # Check if all dependencies are completed
            all_deps_complete = True
            for dep_id in task.depends_on:
                dep_task = next((t for t in workflow.tasks if t.id == dep_id), None)
                if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                    all_deps_complete = False
                    break
            
            if all_deps_complete:
                task.status = TaskStatus.READY
                ready_tasks.append(task)
        
        return ready_tasks

    def _should_execute_task(self, task: Task, workflow: Workflow) -> bool:
        """Check if task should execute based on conditions"""
        if not task.condition:
            return True
        
        # Simple condition evaluation
        context = workflow.context.copy()
        
        # Add results from completed tasks to context
        for completed_task in workflow.tasks:
            if completed_task.status == TaskStatus.COMPLETED:
                context[f"{completed_task.id}_result"] = completed_task.result
        
        try:
            # Simple condition parsing (expand as needed)
            if task.condition.startswith("result("):
                # e.g., "result(spam_detection) > 0.5"
                return eval(task.condition.replace("result(", "context.get('").replace(")", "_result', 0)"))
            
            return eval(task.condition, {"__builtins__": {}}, context)
        except:
            logger.warning(f"Failed to evaluate condition for task {task.id}: {task.condition}")
            return True

    async def _execute_task(self, task: Task, workflow: Workflow):
        """Execute a single task with error handling and callbacks"""
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        
        # Execute on_start callbacks
        await self._execute_callbacks(task.callbacks.get('on_start', []), task, workflow)
        
        try:
            # Get task function
            task_func = self.task_functions.get(task.function)
            if not task_func:
                raise ValueError(f"Unknown task function: {task.function}")
            
            # Execute task
            logger.info(f"Executing task: {task.name}")
            result = await task_func(task.params, workflow.context)
            
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            
            # Update metrics
            execution_time = (task.completed_at - task.started_at).total_seconds() * 1000  # Convert to milliseconds
            await self.task_manager.update_metrics({
                'task_id': task.id,
                'status': 'completed',
                'execution_time': execution_time
            })
            
            # Execute on_success callbacks
            await self._execute_callbacks(task.callbacks.get('on_success', []), task, workflow)
            
            logger.info(f"Task completed successfully: {task.name}")
            
        except Exception as e:
            error_msg = str(e)
            task.error = error_msg
            task.retry_count += 1
            
            logger.error(f"Task failed: {task.name} - {error_msg}")
            
            # Execute on_failure callbacks
            await self._execute_callbacks(task.callbacks.get('on_failure', []), task, workflow)
            
            # Handle retry logic
            if task.retry_count <= task.max_retries:
                await self._handle_retry(task)
            else:
                task.status = TaskStatus.FAILED
                task.completed_at = datetime.now()
                
                # Update metrics for failed task
                execution_time = (task.completed_at - task.started_at).total_seconds() * 1000 if task.started_at else 0
                await self.task_manager.update_metrics({
                    'task_id': task.id,
                    'status': 'failed',
                    'execution_time': execution_time
                })
        
        finally:
            # Execute on_completion callbacks
            await self._execute_callbacks(task.callbacks.get('on_completion', []), task, workflow)

    async def _handle_retry(self, task: Task):
        """Handle task retry with different strategies"""
        delay = 0
        
        if task.retry_strategy == RetryStrategy.IMMEDIATE:
            delay = 0
        elif task.retry_strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = 2 ** task.retry_count
        elif task.retry_strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = task.retry_count * 2
        elif task.retry_strategy == RetryStrategy.CIRCUIT_BREAKER:
            # Simple circuit breaker - wait longer after multiple failures
            delay = min(60, task.retry_count * 10)
        
        if delay > 0:
            logger.info(f"Retrying task {task.name} in {delay} seconds (attempt {task.retry_count + 1})")
            await asyncio.sleep(delay)
        
        task.status = TaskStatus.PENDING

    async def _execute_callbacks(self, callback_names: List[str], task: Task, workflow: Workflow):
        """Execute callbacks for task events"""
        for callback_name in callback_names:
            callback_func = self.callback_functions.get(callback_name)
            if callback_func:
                try:
                    await callback_func(task, workflow)
                except Exception as e:
                    logger.error(f"Callback {callback_name} failed: {str(e)}")

    def _workflow_complete(self, workflow: Workflow) -> bool:
        """Check if workflow is complete"""
        for task in workflow.tasks:
            if task.status in [TaskStatus.PENDING, TaskStatus.READY, TaskStatus.RUNNING]:
                return False
        return True

    def _has_pending_tasks(self, workflow: Workflow) -> bool:
        """Check if workflow has pending tasks"""
        return any(task.status == TaskStatus.PENDING for task in workflow.tasks)

    def get_workflow_status(self, workflow_id: str) -> Dict:
        """Get current workflow status"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return {}
        
        return {
            'id': workflow.id,
            'name': workflow.name,
            'status': workflow.status.value,
            'created_at': workflow.created_at.isoformat() if workflow.created_at else None,
            'started_at': workflow.started_at.isoformat() if workflow.started_at else None,
            'completed_at': workflow.completed_at.isoformat() if workflow.completed_at else None,
            'tasks': [{
                'id': task.id,
                'name': task.name,
                'status': task.status.value,
                'result': task.result,
                'error': task.error,
                'retry_count': task.retry_count,
                'started_at': task.started_at.isoformat() if task.started_at else None,
                'completed_at': task.completed_at.isoformat() if task.completed_at else None,
            } for task in workflow.tasks]
        }

    # Built-in task functions
    async def _process_payment(self, params: Dict, context: Dict):
        """Simulate payment processing"""
        await asyncio.sleep(1)  # Simulate processing time
        amount = params.get('amount', 100)
        if amount < 0:
            raise ValueError("Invalid payment amount")
        return {'transaction_id': f'txn_{uuid.uuid4().hex[:8]}', 'amount': amount}

    async def _reserve_inventory(self, params: Dict, context: Dict):
        """Simulate inventory reservation"""
        await asyncio.sleep(0.5)
        item_id = params.get('item_id', 'default_item')
        quantity = params.get('quantity', 1)
        return {'reservation_id': f'res_{uuid.uuid4().hex[:8]}', 'item_id': item_id, 'quantity': quantity}

    async def _create_shipping_label(self, params: Dict, context: Dict):
        """Simulate shipping label creation"""
        await asyncio.sleep(0.8)
        address = params.get('address', 'Default Address')
        return {'label_id': f'label_{uuid.uuid4().hex[:8]}', 'tracking_number': f'track_{uuid.uuid4().hex[:8]}'}

    async def _send_notification(self, params: Dict, context: Dict):
        """Simulate sending notification"""
        await asyncio.sleep(0.3)
        recipient = params.get('recipient', 'user@example.com')
        message = params.get('message', 'Order processed successfully')
        return {'notification_id': f'notif_{uuid.uuid4().hex[:8]}', 'sent_to': recipient}

    async def _validate_content(self, params: Dict, context: Dict):
        """Simulate content validation"""
        await asyncio.sleep(0.5)
        content = params.get('content', '')
        is_valid = len(content) > 10  # Simple validation
        return {'valid': is_valid, 'content_length': len(content)}

    async def _detect_spam(self, params: Dict, context: Dict):
        """Simulate spam detection"""
        await asyncio.sleep(0.7)
        content = params.get('content', '')
        # Simple spam score simulation
        spam_score = min(1.0, len(content.lower().split('spam')) * 0.3)
        return {'spam_score': spam_score, 'is_spam': spam_score > 0.5}

    async def _manual_review(self, params: Dict, context: Dict):
        """Simulate manual review"""
        await asyncio.sleep(2)  # Longer processing time
        return {'reviewed': True, 'approved': True, 'reviewer': 'moderator'}

    async def _publish_content(self, params: Dict, context: Dict):
        """Simulate content publishing"""
        await asyncio.sleep(0.5)
        return {'published': True, 'url': f'https://example.com/post/{uuid.uuid4().hex[:8]}'}

    async def _invalidate_cache(self, params: Dict, context: Dict):
        """Simulate cache invalidation"""
        await asyncio.sleep(0.2)
        cache_keys = params.get('cache_keys', ['default'])
        return {'invalidated_keys': cache_keys, 'timestamp': datetime.now().isoformat()}

    async def _post_to_social(self, params: Dict, context: Dict):
        """Simulate social media posting"""
        await asyncio.sleep(1)
        platform = params.get('platform', 'twitter')
        return {'posted': True, 'platform': platform, 'post_id': f'{platform}_{uuid.uuid4().hex[:8]}'}

    # Callback functions
    async def _log_start(self, task: Task, workflow: Workflow):
        logger.info(f"Task started: {task.name} in workflow {workflow.name}")

    async def _log_success(self, task: Task, workflow: Workflow):
        logger.info(f"Task succeeded: {task.name} with result {task.result}")

    async def _log_failure(self, task: Task, workflow: Workflow):
        logger.error(f"Task failed: {task.name} with error {task.error}")

    async def _send_alert(self, task: Task, workflow: Workflow):
        logger.warning(f"ALERT: Task {task.name} in workflow {workflow.name} requires attention")
