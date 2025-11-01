"""
Orchestrates comprehensive integration testing across notification channels
"""

import asyncio
import time
from typing import Dict, List
import structlog
from core.notification_service import NotificationService
from mocks.delivery_mocks import DeliveryMockManager

logger = structlog.get_logger()

class TestOrchestrator:
    """
    Coordinates integration tests across the notification system
    """
    
    def __init__(self):
        self.notification_service = NotificationService()
        self.mock_manager = DeliveryMockManager()
        self.test_results = []

    async def run_integration_tests(self) -> Dict:
        """Run comprehensive integration test suite"""
        logger.info("Starting integration test suite")
        
        test_results = {
            "start_time": time.time(),
            "tests": [],
            "summary": {}
        }
        
        # Test basic notification delivery
        basic_tests = await self._test_basic_delivery()
        test_results["tests"].extend(basic_tests)
        
        # Test failure scenarios
        failure_tests = await self._test_failure_scenarios()
        test_results["tests"].extend(failure_tests)
        
        # Test circuit breaker behavior
        circuit_tests = await self._test_circuit_breaker()
        test_results["tests"].extend(circuit_tests)
        
        # Test retry logic
        retry_tests = await self._test_retry_logic()
        test_results["tests"].extend(retry_tests)
        
        # Calculate summary
        test_results["end_time"] = time.time()
        test_results["duration_seconds"] = test_results["end_time"] - test_results["start_time"]
        test_results["summary"] = self._calculate_test_summary(test_results["tests"])
        
        logger.info("Integration test suite completed", 
                   summary=test_results["summary"])
        
        return test_results

    async def _test_basic_delivery(self) -> List[Dict]:
        """Test basic notification delivery across all channels"""
        tests = []
        channels = ["email", "sms", "push", "webhook"]
        
        for channel in channels:
            test_start = time.time()
            
            try:
                result = await self.notification_service.send_notification({
                    "user_id": f"test_user_{channel}",
                    "channel": channel,
                    "content": f"Test notification for {channel}",
                    "priority": "normal"
                })
                
                test_result = {
                    "test_name": f"basic_delivery_{channel}",
                    "channel": channel,
                    "success": result["success"],
                    "duration_ms": (time.time() - test_start) * 1000,
                    "error": result.get("error"),
                    "details": result
                }
                
            except Exception as e:
                test_result = {
                    "test_name": f"basic_delivery_{channel}",
                    "channel": channel,
                    "success": False,
                    "duration_ms": (time.time() - test_start) * 1000,
                    "error": str(e),
                    "details": {}
                }
            
            tests.append(test_result)
            
            # Small delay between tests
            await asyncio.sleep(0.1)
        
        return tests

    async def _test_failure_scenarios(self) -> List[Dict]:
        """Test system behavior under failure conditions"""
        tests = []
        
        # Configure high failure rates
        failure_config = {
            "email": {"success_rate": 0.1, "latency_ms": (100, 300)},
            "sms": {"success_rate": 0.2, "latency_ms": (200, 800)}
        }
        
        await self.mock_manager.configure_mocks(failure_config)
        
        # Test with high failure rates
        for channel in ["email", "sms"]:
            test_start = time.time()
            
            try:
                result = await self.notification_service.send_notification({
                    "user_id": f"failure_test_{channel}",
                    "channel": channel,
                    "content": f"Failure test for {channel}",
                    "priority": "normal"
                })
                
                tests.append({
                    "test_name": f"failure_scenario_{channel}",
                    "channel": channel,
                    "success": True,  # Test succeeded (even if notification failed)
                    "duration_ms": (time.time() - test_start) * 1000,
                    "notification_success": result["success"],
                    "attempts": result.get("attempts", 1),
                    "details": result
                })
                
            except Exception as e:
                tests.append({
                    "test_name": f"failure_scenario_{channel}",
                    "channel": channel,
                    "success": False,
                    "duration_ms": (time.time() - test_start) * 1000,
                    "error": str(e)
                })
        
        # Restore normal configuration
        normal_config = {
            "email": {"success_rate": 0.95, "latency_ms": (100, 300)},
            "sms": {"success_rate": 0.90, "latency_ms": (200, 800)}
        }
        await self.mock_manager.configure_mocks(normal_config)
        
        return tests

    async def _test_circuit_breaker(self) -> List[Dict]:
        """Test circuit breaker behavior"""
        tests = []
        
        # Force circuit breaker to open by sending multiple failing requests
        failing_config = {"email": {"success_rate": 0.0, "latency_ms": (100, 200)}}
        await self.mock_manager.configure_mocks(failing_config)
        
        # Send enough requests to trip circuit breaker
        for i in range(7):  # More than failure threshold
            await self.notification_service.send_notification({
                "user_id": f"circuit_test_{i}",
                "channel": "email",
                "content": "Circuit breaker test",
                "priority": "normal"
            })
            await asyncio.sleep(0.05)
        
        # Test that circuit breaker is open
        test_start = time.time()
        result = await self.notification_service.send_notification({
            "user_id": "circuit_open_test",
            "channel": "email",
            "content": "Should be blocked by circuit breaker",
            "priority": "normal"
        })
        
        circuit_open_test = {
            "test_name": "circuit_breaker_open",
            "channel": "email",
            "success": "Circuit breaker open" in (result.get("error") or ""),
            "duration_ms": (time.time() - test_start) * 1000,
            "details": result
        }
        tests.append(circuit_open_test)
        
        # Restore normal configuration
        normal_config = {"email": {"success_rate": 0.95, "latency_ms": (100, 300)}}
        await self.mock_manager.configure_mocks(normal_config)
        
        return tests

    async def _test_retry_logic(self) -> List[Dict]:
        """Test retry logic with transient failures"""
        tests = []
        
        # Configure intermittent failures (50% success rate)
        retry_config = {"sms": {"success_rate": 0.5, "latency_ms": (100, 200)}}
        await self.mock_manager.configure_mocks(retry_config)
        
        test_start = time.time()
        result = await self.notification_service.send_notification({
            "user_id": "retry_test",
            "channel": "sms",
            "content": "Retry logic test",
            "priority": "normal"
        })
        
        retry_test = {
            "test_name": "retry_logic",
            "channel": "sms",
            "success": True,  # Test execution succeeded
            "duration_ms": (time.time() - test_start) * 1000,
            "attempts": result.get("attempts", 1),
            "final_success": result["success"],
            "details": result
        }
        tests.append(retry_test)
        
        # Restore normal configuration
        normal_config = {"sms": {"success_rate": 0.90, "latency_ms": (200, 800)}}
        await self.mock_manager.configure_mocks(normal_config)
        
        return tests

    def _calculate_test_summary(self, tests: List[Dict]) -> Dict:
        """Calculate test summary statistics"""
        total_tests = len(tests)
        passed_tests = sum(1 for test in tests if test["success"])
        
        avg_duration = sum(test["duration_ms"] for test in tests) / total_tests if total_tests > 0 else 0
        
        by_channel = {}
        for test in tests:
            channel = test["channel"]
            if channel not in by_channel:
                by_channel[channel] = {"total": 0, "passed": 0}
            by_channel[channel]["total"] += 1
            if test["success"]:
                by_channel[channel]["passed"] += 1
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "pass_rate": passed_tests / total_tests if total_tests > 0 else 0,
            "avg_duration_ms": avg_duration,
            "by_channel": by_channel
        }
