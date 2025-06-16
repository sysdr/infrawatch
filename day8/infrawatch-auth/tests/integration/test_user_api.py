import pytest
import json
from app.models.user import User
from app.factories.user_factory import UserFactory

class TestUserAPI:
    
    def test_create_user_success(self, client, db_session):
        """Test successful user creation"""
        user_data = {
            'email': 'newuser@infrawatch.com',
            'password': 'TestPass123!',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = client.post('/api/users', 
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'user' in data
        assert data['user']['email'] == user_data['email']
        assert 'password_hash' not in data['user']
    
    def test_create_user_duplicate_email(self, client, db_session):
        """Test user creation with duplicate email"""
        # Create first user
        user = UserFactory(email='duplicate@infrawatch.com')
        
        user_data = {
            'email': 'duplicate@infrawatch.com',
            'password': 'TestPass123!'
        }
        
        response = client.post('/api/users',
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        assert response.status_code == 409
        data = json.loads(response.data)
        assert 'already exists' in data['error']
    
    def test_create_user_invalid_email(self, client, db_session):
        """Test user creation with invalid email"""
        user_data = {
            'email': 'invalid-email',
            'password': 'TestPass123!'
        }
        
        response = client.post('/api/users',
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Invalid email format' in data['error']
    
    def test_create_user_weak_password(self, client, db_session):
        """Test user creation with weak password"""
        user_data = {
            'email': 'test@infrawatch.com',
            'password': 'weak'
        }
        
        response = client.post('/api/users',
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Password validation failed' in data['error']
    
    def test_get_user_success(self, client, db_session):
        """Test successful user retrieval"""
        user = UserFactory()
        
        response = client.get(f'/api/users/{user.id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['user']['email'] == user.email
    
    def test_get_user_not_found(self, client, db_session):
        """Test user retrieval with invalid ID"""
        response = client.get('/api/users/nonexistent-id')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'User not found' in data['error']
    
    def test_list_users(self, client, db_session):
        """Test user listing with pagination"""
        # Create multiple users
        users = UserFactory.create_batch(5)
        
        response = client.get('/api/users?page=1&per_page=3')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['users']) == 3
        assert 'pagination' in data
        assert data['pagination']['total'] == 5
    
    def test_verify_password_success(self, client, db_session):
        """Test successful password verification"""
        user = UserFactory(password='TestPass123!')
        
        verify_data = {
            'email': user.email,
            'password': 'TestPass123!'
        }
        
        response = client.post('/api/users/verify-password',
                             data=json.dumps(verify_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'Password verified successfully' in data['message']
    
    def test_verify_password_invalid(self, client, db_session):
        """Test password verification with wrong password"""
        user = UserFactory(password='TestPass123!')
        
        verify_data = {
            'email': user.email,
            'password': 'WrongPassword'
        }
        
        response = client.post('/api/users/verify-password',
                             data=json.dumps(verify_data),
                             content_type='application/json')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'Invalid credentials' in data['error']
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['service'] == 'infrawatch-auth'
