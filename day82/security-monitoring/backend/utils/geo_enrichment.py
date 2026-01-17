"""Geographic enrichment for security events"""
from typing import Dict
import random

async def enrich_with_geo(event: Dict) -> Dict:
    """Enrich event with geolocation data"""
    ip = event.get('ip_address', '')
    
    # Simulated geo lookup (in production, use MaxMind GeoIP2)
    geo_data = _simulate_geo_lookup(ip)
    
    event.update({
        'country': geo_data['country'],
        'city': geo_data['city'],
        'latitude': geo_data['latitude'],
        'longitude': geo_data['longitude']
    })
    
    return event

def _simulate_geo_lookup(ip: str) -> Dict:
    """Simulate geolocation lookup"""
    # Sample locations for testing
    locations = [
        {'country': 'US', 'city': 'San Francisco', 'latitude': 37.7749, 'longitude': -122.4194},
        {'country': 'US', 'city': 'New York', 'latitude': 40.7128, 'longitude': -74.0060},
        {'country': 'UK', 'city': 'London', 'latitude': 51.5074, 'longitude': -0.1278},
        {'country': 'JP', 'city': 'Tokyo', 'latitude': 35.6762, 'longitude': 139.6503},
        {'country': 'DE', 'city': 'Berlin', 'latitude': 52.5200, 'longitude': 13.4050}
    ]
    
    # Deterministic selection based on IP
    index = sum(ord(c) for c in ip) % len(locations)
    return locations[index]
