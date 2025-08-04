import pytest
import asyncio
from app.validators.network import NetworkValidator, HealthChecker, ServerDiscovery

class TestNetworkValidator:
    
    def test_valid_ip_address(self):
        validator = NetworkValidator()
        valid, message = validator.validate_ip_address("192.168.1.1")
        assert valid == True
        assert "Valid" in message
    
    def test_invalid_ip_address(self):
        validator = NetworkValidator()
        valid, message = validator.validate_ip_address("256.256.256.256")
        assert valid == False
        assert "Invalid" in message
    
    def test_valid_hostname(self):
        validator = NetworkValidator()
        valid, message = validator.validate_hostname("example.com")
        assert valid == True
        assert "Valid" in message
    
    def test_invalid_hostname(self):
        validator = NetworkValidator()
        valid, message = validator.validate_hostname("invalid..hostname")
        assert valid == False

class TestHealthChecker:
    
    @pytest.mark.asyncio
    async def test_http_health_check(self):
        checker = HealthChecker()
        # Test with a public endpoint
        result = await checker.http_health_check("https://httpbin.org/status/200")
        assert "status" in result
        assert "response_time" in result

if __name__ == "__main__":
    pytest.main([__file__])
