import pytest
import asyncio
from backend.app.orchestration.workflow_engine import WorkflowEngine, TaskStatus
from backend.app.orchestration.task_manager import TaskManager

@pytest.mark.asyncio
async def test_workflow_creation():
    """Test workflow creation and validation"""
    task_manager = TaskManager()
    engine = WorkflowEngine(task_manager)
    
    workflow_def = {
        "name": "Test Workflow",
        "tasks": [
            {
                "id": "task1",
                "name": "Task 1",
                "function": "process_payment",
                "depends_on": [],
                "params": {"amount": 100}
            },
            {
                "id": "task2", 
                "name": "Task 2",
                "function": "reserve_inventory",
                "depends_on": ["task1"],
                "params": {"item_id": "test_item"}
            }
        ]
    }
    
    workflow_id = await engine.create_workflow(workflow_def)
    assert workflow_id in engine.workflows
    
    workflow = engine.workflows[workflow_id]
    assert workflow.name == "Test Workflow"
    assert len(workflow.tasks) == 2

@pytest.mark.asyncio
async def test_workflow_execution():
    """Test workflow execution with dependencies"""
    task_manager = TaskManager()
    engine = WorkflowEngine(task_manager)
    
    workflow_def = {
        "name": "Execution Test",
        "tasks": [
            {
                "id": "payment",
                "name": "Process Payment",
                "function": "process_payment",
                "depends_on": [],
                "params": {"amount": 50}
            }
        ]
    }
    
    workflow_id = await engine.create_workflow(workflow_def)
    await engine.execute_workflow(workflow_id)
    
    workflow = engine.workflows[workflow_id]
    assert workflow.status == TaskStatus.COMPLETED
    assert workflow.tasks[0].status == TaskStatus.COMPLETED

@pytest.mark.asyncio
async def test_conditional_execution():
    """Test conditional task execution"""
    task_manager = TaskManager()
    engine = WorkflowEngine(task_manager)
    
    workflow_def = {
        "name": "Conditional Test",
        "tasks": [
            {
                "id": "detect_spam",
                "name": "Detect Spam",
                "function": "detect_spam",
                "depends_on": [],
                "params": {"content": "normal content"}
            },
            {
                "id": "manual_review",
                "name": "Manual Review", 
                "function": "manual_review",
                "depends_on": ["detect_spam"],
                "condition": "detect_spam_result['spam_score'] > 0.5",
                "params": {}
            }
        ]
    }
    
    workflow_id = await engine.create_workflow(workflow_def)
    await engine.execute_workflow(workflow_id)
    
    workflow = engine.workflows[workflow_id]
    manual_review_task = next(t for t in workflow.tasks if t.id == "manual_review")
    
    # Should be skipped because spam_score is low
    assert manual_review_task.status in [TaskStatus.SKIPPED, TaskStatus.PENDING]

def test_workflow_validation():
    """Test workflow validation for cycles"""
    task_manager = TaskManager()
    engine = WorkflowEngine(task_manager)
    
    # Create workflow with cycle
    workflow_def = {
        "name": "Cyclic Workflow",
        "tasks": [
            {
                "id": "task1",
                "name": "Task 1",
                "function": "process_payment",
                "depends_on": ["task2"],
                "params": {}
            },
            {
                "id": "task2",
                "name": "Task 2", 
                "function": "reserve_inventory",
                "depends_on": ["task1"],
                "params": {}
            }
        ]
    }
    
    with pytest.raises(ValueError, match="Invalid workflow"):
        asyncio.run(engine.create_workflow(workflow_def))

if __name__ == "__main__":
    pytest.main([__file__])
