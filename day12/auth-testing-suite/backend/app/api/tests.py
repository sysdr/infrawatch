from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import subprocess
import asyncio
import json
from typing import Dict, Any

from app.core.database import get_db
from app.dependencies import get_current_user

router = APIRouter()

@router.post("/unit")
async def run_unit_tests(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Run unit tests and return results"""
    try:
        # Run pytest for unit tests
        process = await asyncio.create_subprocess_exec(
            "pytest", "tests/unit/", "-v",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            return {
                "status": "passed",
                "message": "Unit tests completed successfully",
                "details": stdout.decode()
            }
        else:
            return {
                "status": "failed",
                "message": "Unit tests failed",
                "details": stderr.decode()
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run unit tests: {str(e)}"
        )

@router.post("/integration")
async def run_integration_tests(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Run integration tests and return results"""
    try:
        # Run pytest for integration tests
        process = await asyncio.create_subprocess_exec(
            "pytest", "tests/integration/", "-v",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            return {
                "status": "passed",
                "message": "Integration tests completed successfully",
                "details": stdout.decode()
            }
        else:
            return {
                "status": "failed",
                "message": "Integration tests failed",
                "details": stderr.decode()
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run integration tests: {str(e)}"
        )

@router.post("/security")
async def run_security_tests(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Run security tests and return results"""
    try:
        # Run pytest for security tests
        process = await asyncio.create_subprocess_exec(
            "pytest", "tests/security/", "-v",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            return {
                "status": "passed",
                "message": "Security tests completed successfully",
                "details": stdout.decode()
            }
        else:
            return {
                "status": "failed",
                "message": "Security tests failed",
                "details": stderr.decode()
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run security tests: {str(e)}"
        )

@router.post("/performance")
async def run_performance_tests(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Run performance tests and return results"""
    try:
        # Run locust for performance tests
        process = await asyncio.create_subprocess_exec(
            "locust", "-f", "tests/performance/locustfile.py", 
            "--host=http://localhost:8000", "--headless", "--users", "10", 
            "--spawn-rate", "2", "--run-time", "30s",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            return {
                "status": "passed",
                "message": "Performance tests completed successfully",
                "details": stdout.decode()
            }
        else:
            return {
                "status": "failed",
                "message": "Performance tests failed",
                "details": stderr.decode()
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run performance tests: {str(e)}"
        )

@router.get("/coverage")
async def get_test_coverage(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get test coverage statistics"""
    try:
        # Run pytest with coverage
        process = await asyncio.create_subprocess_exec(
            "pytest", "--cov=app", "--cov-report=json",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            # Parse coverage report
            coverage_data = json.loads(stdout.decode())
            return {
                "overall_coverage": coverage_data.get("totals", {}).get("percent_covered", 0),
                "details": coverage_data
            }
        else:
            return {
                "overall_coverage": 0,
                "error": stderr.decode()
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get test coverage: {str(e)}"
        ) 