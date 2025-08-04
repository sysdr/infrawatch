import re
import socket
import ipaddress
import ssl
import asyncio
import httpx
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from cryptography import x509
from cryptography.hazmat.backends import default_backend
import validators
import ping3

class NetworkValidator:
    
    @staticmethod
    def validate_ip_address(ip: str) -> Tuple[bool, str]:
        """Validate IP address format and type"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            if ip_obj.is_private:
                return True, f"Valid private IP: {ip}"
            elif ip_obj.is_global:
                return True, f"Valid public IP: {ip}"
            else:
                return True, f"Valid IP: {ip}"
        except ValueError as e:
            return False, f"Invalid IP address: {str(e)}"
    
    @staticmethod
    def validate_hostname(hostname: str) -> Tuple[bool, str]:
        """Validate hostname format"""
        if not hostname or len(hostname) > 253:
            return False, "Hostname too long or empty"
        
        if hostname[-1] == ".":
            hostname = hostname[:-1]
        
        allowed = re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$")
        
        if all(allowed.match(label) for label in hostname.split(".")):
            return True, f"Valid hostname: {hostname}"
        return False, "Invalid hostname format"
    
    @staticmethod
    async def check_connectivity(host: str, port: int = 80, timeout: int = 5) -> Dict[str, Any]:
        """Check network connectivity to host:port"""
        result = {
            "reachable": False,
            "response_time": 0.0,
            "error": None
        }
        
        try:
            start_time = datetime.now()
            
            # Try ping first
            ping_result = ping3.ping(host, timeout=timeout)
            if ping_result is not None:
                result["ping_time"] = ping_result * 1000  # Convert to ms
            
            # Try TCP connection
            try:
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(host, port),
                    timeout=timeout
                )
                writer.close()
                await writer.wait_closed()
                
                end_time = datetime.now()
                result["response_time"] = (end_time - start_time).total_seconds() * 1000
                result["reachable"] = True
                
            except Exception as e:
                result["error"] = f"TCP connection failed: {str(e)}"
                
        except Exception as e:
            result["error"] = f"Connectivity check failed: {str(e)}"
            
        return result

class HealthChecker:
    
    def __init__(self):
        self.timeout = 10
        
    async def http_health_check(self, url: str) -> Dict[str, Any]:
        """Perform HTTP health check"""
        result = {
            "status": "unknown",
            "response_time": 0.0,
            "status_code": None,
            "error": None
        }
        
        try:
            start_time = datetime.now()
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                
            end_time = datetime.now()
            result["response_time"] = (end_time - start_time).total_seconds() * 1000
            result["status_code"] = response.status_code
            
            if 200 <= response.status_code < 300:
                result["status"] = "healthy"
            elif 400 <= response.status_code < 500:
                result["status"] = "degraded"
            else:
                result["status"] = "unhealthy"
                
        except Exception as e:
            result["status"] = "unreachable"
            result["error"] = str(e)
            
        return result
    
    async def ssl_certificate_check(self, hostname: str, port: int = 443) -> Dict[str, Any]:
        """Check SSL certificate validity"""
        result = {
            "valid": False,
            "expiry_date": None,
            "days_until_expiry": None,
            "issuer": None,
            "error": None
        }
        
        try:
            context = ssl.create_default_context()
            
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert_der = ssock.getpeercert(binary_form=True)
                    
            cert = x509.load_der_x509_certificate(cert_der, default_backend())
            
            result["valid"] = True
            result["expiry_date"] = cert.not_valid_after
            result["issuer"] = cert.issuer.rfc4514_string()
            
            days_until_expiry = (cert.not_valid_after - datetime.now()).days
            result["days_until_expiry"] = days_until_expiry
            
            if days_until_expiry < 30:
                result["warning"] = "Certificate expires within 30 days"
                
        except Exception as e:
            result["error"] = str(e)
            
        return result

class ServerDiscovery:
    
    @staticmethod
    async def scan_network_range(network: str, ports: list = [80, 443, 22, 8080]) -> list:
        """Discover servers in network range"""
        discovered = []
        
        try:
            network_obj = ipaddress.IPv4Network(network, strict=False)
            
            # Limit scan for demo purposes
            hosts_to_scan = list(network_obj.hosts())[:10]
            
            for host in hosts_to_scan:
                host_str = str(host)
                
                # Quick ping check
                if ping3.ping(host_str, timeout=1):
                    server_info = {
                        "ip": host_str,
                        "hostname": await ServerDiscovery._reverse_dns(host_str),
                        "open_ports": []
                    }
                    
                    # Check common ports
                    for port in ports:
                        if await ServerDiscovery._check_port(host_str, port):
                            server_info["open_ports"].append(port)
                    
                    if server_info["open_ports"]:
                        discovered.append(server_info)
                        
        except Exception as e:
            print(f"Network scan error: {e}")
            
        return discovered
    
    @staticmethod
    async def _reverse_dns(ip: str) -> Optional[str]:
        """Perform reverse DNS lookup"""
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            return hostname
        except:
            return None
    
    @staticmethod
    async def _check_port(host: str, port: int) -> bool:
        """Check if port is open"""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=2
            )
            writer.close()
            await writer.wait_closed()
            return True
        except:
            return False
