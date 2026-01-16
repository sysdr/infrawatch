import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend')))

from security.ip_whitelist import IPWhitelist

def test_ip_whitelisted_single_cidr():
    whitelist = ["192.168.1.0/24"]
    
    assert IPWhitelist.is_ip_whitelisted("192.168.1.50", whitelist) is True
    assert IPWhitelist.is_ip_whitelisted("192.168.2.50", whitelist) is False

def test_ip_whitelisted_multiple_cidrs():
    whitelist = ["192.168.1.0/24", "10.0.0.0/8"]
    
    assert IPWhitelist.is_ip_whitelisted("192.168.1.100", whitelist) is True
    assert IPWhitelist.is_ip_whitelisted("10.5.10.20", whitelist) is True
    assert IPWhitelist.is_ip_whitelisted("172.16.0.1", whitelist) is False

def test_ip_whitelisted_empty_list():
    whitelist = []
    
    # Empty whitelist allows all IPs
    assert IPWhitelist.is_ip_whitelisted("192.168.1.1", whitelist) is True
    assert IPWhitelist.is_ip_whitelisted("8.8.8.8", whitelist) is True

def test_validate_cidr():
    assert IPWhitelist.validate_cidr("192.168.1.0/24") is True
    assert IPWhitelist.validate_cidr("10.0.0.0/8") is True
    assert IPWhitelist.validate_cidr("invalid-cidr") is False
    assert IPWhitelist.validate_cidr("192.168.1.500/24") is False
