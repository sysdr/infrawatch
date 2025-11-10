import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from server import app, socketio, generate_token, verify_token
import socketio as sio_client

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'

def test_login_endpoint(client):
    """Test login endpoint"""
    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert 'token' in data

def test_token_generation():
    """Test JWT token generation and verification"""
    token = generate_token('user_123', 'testuser')
    assert token is not None
    
    payload = verify_token(token)
    assert payload is not None
    assert payload['user_id'] == 'user_123'
    assert payload['username'] == 'testuser'

def test_stats_endpoint(client):
    """Test stats endpoint"""
    response = client.get('/api/stats')
    assert response.status_code == 200
    data = response.get_json()
    assert 'stats' in data
    assert 'active_connections' in data

def test_invalid_login(client):
    """Test login with missing credentials"""
    response = client.post('/api/auth/login', json={})
    assert response.status_code == 401

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
