import pytest
import json
from app import create_app, db
from models.user import User

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def sample_user(app):
    with app.app_context():
        user = User(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            role='user'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user

class TestAuthentication:
    def test_register_user(self, client):
        """Test user registration"""
        response = client.post('/auth/register', 
            json={
                'email': 'newuser@example.com',
                'password': 'password123',
                'first_name': 'New',
                'last_name': 'User'
            })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'User created successfully'
        assert data['user']['email'] == 'newuser@example.com'
    
    def test_register_duplicate_email(self, client, sample_user):
        """Test registration with existing email"""
        response = client.post('/auth/register',
            json={
                'email': 'test@example.com',
                'password': 'password123',
                'first_name': 'Another',
                'last_name': 'User'
            })
        
        assert response.status_code == 409
        data = json.loads(response.data)
        assert 'already registered' in data['error']
    
    def test_login_success(self, client, sample_user):
        """Test successful login"""
        response = client.post('/auth/login',
            json={
                'email': 'test@example.com',
                'password': 'password123'
            })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['user']['email'] == 'test@example.com'
    
    def test_login_invalid_credentials(self, client, sample_user):
        """Test login with invalid credentials"""
        response = client.post('/auth/login',
            json={
                'email': 'test@example.com',
                'password': 'wrongpassword'
            })
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'Invalid credentials' in data['error']
    
    def test_protected_endpoint_without_token(self, client):
        """Test accessing protected endpoint without token"""
        response = client.get('/auth/profile')
        assert response.status_code == 401
    
    def test_protected_endpoint_with_token(self, client, sample_user):
        """Test accessing protected endpoint with valid token"""
        # Login first
        login_response = client.post('/auth/login',
            json={
                'email': 'test@example.com',
                'password': 'password123'
            })
        
        token = json.loads(login_response.data)['access_token']
        
        # Access protected endpoint
        response = client.get('/auth/profile',
            headers={'Authorization': f'Bearer {token}'})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['user']['email'] == 'test@example.com'
    
    def test_token_refresh(self, client, sample_user):
        """Test token refresh functionality"""
        # Login first
        login_response = client.post('/auth/login',
            json={
                'email': 'test@example.com',
                'password': 'password123'
            })
        
        refresh_token = json.loads(login_response.data)['refresh_token']
        
        # Refresh token
        response = client.post('/auth/refresh',
            json={'refresh_token': refresh_token})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
        assert 'refresh_token' in data
    
    def test_logout(self, client, sample_user):
        """Test logout functionality"""
        # Login first
        login_response = client.post('/auth/login',
            json={
                'email': 'test@example.com',
                'password': 'password123'
            })
        
        token = json.loads(login_response.data)['access_token']
        
        # Logout
        response = client.post('/auth/logout',
            headers={'Authorization': f'Bearer {token}'})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Logout successful'
