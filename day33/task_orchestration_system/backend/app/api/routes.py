from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any
import asyncio

router = APIRouter()

@router.post("/workflows")
async def create_workflow(request: Request, workflow_def: Dict[str, Any]):
    """Create a new workflow"""
    try:
        workflow_engine = request.app.state.workflow_engine
        workflow_id = await workflow_engine.create_workflow(workflow_def)
        return {"workflow_id": workflow_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/workflows/{workflow_id}/execute")
async def execute_workflow(request: Request, workflow_id: str):
    """Execute a workflow"""
    try:
        workflow_engine = request.app.state.workflow_engine
        # Execute workflow in background
        asyncio.create_task(workflow_engine.execute_workflow(workflow_id))
        return {"workflow_id": workflow_id, "status": "started"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/workflows/{workflow_id}/status")
async def get_workflow_status(request: Request, workflow_id: str):
    """Get workflow status"""
    workflow_engine = request.app.state.workflow_engine
    status = workflow_engine.get_workflow_status(workflow_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return status

@router.get("/workflows")
async def list_workflows(request: Request):
    """List all workflows"""
    workflow_engine = request.app.state.workflow_engine
    workflows = []
    
    for workflow_id in workflow_engine.workflows:
        status = workflow_engine.get_workflow_status(workflow_id)
        workflows.append(status)
    
    return {"workflows": workflows}

@router.get("/metrics")
async def get_metrics(request: Request):
    """Get task metrics"""
    task_manager = request.app.state.task_manager
    return task_manager.get_metrics()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

@router.post("/workflows/samples/ecommerce")
async def create_ecommerce_workflow(request: Request):
    """Create sample e-commerce workflow"""
    workflow_def = {
        "name": "E-Commerce Order Processing",
        "tasks": [
            {
                "id": "payment",
                "name": "Process Payment",
                "function": "process_payment",
                "depends_on": [],
                "params": {"amount": 99.99},
                "callbacks": {
                    "on_start": ["log_start"],
                    "on_success": ["log_success"],
                    "on_failure": ["log_failure", "send_alert"]
                }
            },
            {
                "id": "inventory",
                "name": "Reserve Inventory",
                "function": "reserve_inventory",
                "depends_on": ["payment"],
                "params": {"item_id": "product_123", "quantity": 1},
                "callbacks": {
                    "on_start": ["log_start"],
                    "on_success": ["log_success"],
                    "on_failure": ["log_failure"]
                }
            },
            {
                "id": "shipping",
                "name": "Create Shipping Label",
                "function": "create_shipping_label",
                "depends_on": ["inventory"],
                "params": {"address": "123 Main St, City, State"},
                "retry_strategy": "exponential_backoff",
                "callbacks": {
                    "on_start": ["log_start"],
                    "on_success": ["log_success"]
                }
            },
            {
                "id": "notification",
                "name": "Send Notification",
                "function": "send_notification",
                "depends_on": ["payment"],
                "params": {"recipient": "customer@example.com", "message": "Order confirmed"},
                "callbacks": {
                    "on_start": ["log_start"],
                    "on_completion": ["log_success"]
                }
            }
        ]
    }
    
    workflow_engine = request.app.state.workflow_engine
    workflow_id = await workflow_engine.create_workflow(workflow_def)
    return {"workflow_id": workflow_id, "status": "created", "type": "ecommerce"}

@router.post("/workflows/samples/blog")
async def create_blog_workflow(request: Request):
    """Create sample blog publishing workflow"""
    workflow_def = {
        "name": "Blog Publishing Workflow",
        "tasks": [
            {
                "id": "validate",
                "name": "Validate Content",
                "function": "validate_content",
                "depends_on": [],
                "params": {"content": "This is a sample blog post with enough content to pass validation."},
                "callbacks": {
                    "on_start": ["log_start"],
                    "on_failure": ["send_alert"]
                }
            },
            {
                "id": "spam_detection",
                "name": "Spam Detection",
                "function": "detect_spam",
                "depends_on": ["validate"],
                "params": {"content": "This is a legitimate blog post"},
                "callbacks": {
                    "on_success": ["log_success"]
                }
            },
            {
                "id": "manual_review",
                "name": "Manual Review",
                "function": "manual_review",
                "depends_on": ["spam_detection"],
                "condition": "spam_detection_result['spam_score'] > 0.3",
                "params": {},
                "callbacks": {
                    "on_start": ["log_start"],
                    "on_completion": ["log_success"]
                }
            },
            {
                "id": "publish",
                "name": "Publish Content",
                "function": "publish_content",
                "depends_on": ["spam_detection", "manual_review"],
                "params": {"title": "Sample Blog Post"},
                "callbacks": {
                    "on_success": ["log_success"]
                }
            },
            {
                "id": "cache_invalidation",
                "name": "Invalidate Cache",
                "function": "invalidate_cache",
                "depends_on": ["publish"],
                "params": {"cache_keys": ["blog_posts", "recent_articles"]},
                "retry_strategy": "immediate"
            },
            {
                "id": "social_posting",
                "name": "Post to Social Media",
                "function": "post_to_social",
                "depends_on": ["publish"],
                "params": {"platform": "twitter"},
                "retry_strategy": "exponential_backoff",
                "max_retries": 5
            }
        ]
    }
    
    workflow_engine = request.app.state.workflow_engine
    workflow_id = await workflow_engine.create_workflow(workflow_def)
    return {"workflow_id": workflow_id, "status": "created", "type": "blog"}
