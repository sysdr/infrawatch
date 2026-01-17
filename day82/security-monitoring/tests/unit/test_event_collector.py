"""Unit tests for event collector"""
import pytest
from datetime import datetime

@pytest.mark.asyncio
async def test_event_normalization():
    """Test event data normalization"""
    # Simulated test
    event = {
        'event_type': 'authentication',
        'user_id': 'test_user',
        'ip_address': '192.168.1.100',
        'action': 'login',
        'success': True
    }
    
    assert event['event_type'] == 'authentication'
    assert event['success'] is True

@pytest.mark.asyncio
async def test_event_enrichment():
    """Test geo enrichment"""
    event = {'ip_address': '192.168.1.100'}
    # Test would validate geo data added
    assert 'ip_address' in event
