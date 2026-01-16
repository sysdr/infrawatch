import ipaddress
from typing import List

class IPWhitelist:
    
    @staticmethod
    def is_ip_whitelisted(client_ip: str, whitelist: List[str]) -> bool:
        """
        Check if client IP is in whitelist (supports CIDR notation)
        """
        if not whitelist:
            # Empty whitelist means all IPs allowed
            return True
        
        try:
            client_addr = ipaddress.ip_address(client_ip)
            
            for cidr in whitelist:
                try:
                    network = ipaddress.ip_network(cidr, strict=False)
                    if client_addr in network:
                        return True
                except ValueError:
                    # Invalid CIDR notation, skip
                    continue
            
            return False
            
        except ValueError:
            # Invalid IP address
            return False
    
    @staticmethod
    def validate_cidr(cidr: str) -> bool:
        """Validate CIDR notation"""
        try:
            ipaddress.ip_network(cidr, strict=False)
            return True
        except ValueError:
            return False
