import asyncio
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from ..models.server import Server, HealthCheck
from ..validators.network import NetworkValidator, HealthChecker, ServerDiscovery
import redis
import json
from datetime import datetime

class ValidationService:
    
    def __init__(self, db: Session, redis_client: redis.Redis):
        self.db = db
        self.redis = redis_client
        self.validator = NetworkValidator()
        self.health_checker = HealthChecker()
        self.discovery = ServerDiscovery()
    
    async def validate_server(self, hostname: str, ip_address: str, port: int = 80) -> Dict[str, Any]:
        """Comprehensive server validation"""
        results = {
            "hostname_valid": False,
            "ip_valid": False,
            "connectivity": {},
            "health": {},
            "ssl": {},
            "overall_status": "unknown"
        }
        
        # Validate hostname
        hostname_valid, hostname_msg = self.validator.validate_hostname(hostname)
        results["hostname_valid"] = hostname_valid
        results["hostname_message"] = hostname_msg
        
        # Validate IP
        ip_valid, ip_msg = self.validator.validate_ip_address(ip_address)
        results["ip_valid"] = ip_valid
        results["ip_message"] = ip_msg
        
        if hostname_valid and ip_valid:
            # Check connectivity
            results["connectivity"] = await self.validator.check_connectivity(ip_address, port)
            
            if results["connectivity"]["reachable"]:
                # Health check
                protocol = "https" if port == 443 else "http"
                url = f"{protocol}://{hostname}:{port}"
                results["health"] = await self.health_checker.http_health_check(url)
                
                # SSL check for HTTPS
                if port == 443:
                    results["ssl"] = await self.health_checker.ssl_certificate_check(hostname, port)
        
        # Determine overall status
        if results["connectivity"].get("reachable") and results["health"].get("status") == "healthy":
            results["overall_status"] = "healthy"
        elif results["connectivity"].get("reachable"):
            results["overall_status"] = "degraded"
        else:
            results["overall_status"] = "unreachable"
        
        # Cache results
        cache_key = f"validation:{hostname}:{ip_address}:{port}"
        self.redis.setex(cache_key, 300, json.dumps(results, default=str))
        
        return results
    
    async def continuous_health_monitoring(self, server_id: int):
        """Start continuous health monitoring for a server"""
        server = self.db.query(Server).filter(Server.id == server_id).first()
        if not server:
            return
        
        while server.is_active:
            # Perform health check
            protocol = "https" if server.port == 443 else "http"
            url = f"{protocol}://{server.hostname}:{server.port}"
            health_result = await self.health_checker.http_health_check(url)
            
            # Update server status
            server.status = health_result["status"]
            server.response_time = health_result["response_time"]
            server.last_check = datetime.now()
            
            # Log health check
            health_check = HealthCheck(
                server_id=server.id,
                check_type="http",
                status=health_result["status"],
                response_time=health_result["response_time"],
                details=json.dumps(health_result)
            )
            self.db.add(health_check)
            self.db.commit()
            
            # Wait before next check
            await asyncio.sleep(30)
    
    async def discover_servers(self, network_range: str) -> List[Dict[str, Any]]:
        """Discover servers in network range"""
        discovered = await self.discovery.scan_network_range(network_range)
        
        # Cache discovery results
        cache_key = f"discovery:{network_range}"
        self.redis.setex(cache_key, 900, json.dumps(discovered, default=str))
        
        return discovered
