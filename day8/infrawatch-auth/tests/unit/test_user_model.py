import pytest
from app.models.user import User
from app.factories.user_factory import UserFactory

class TestUserModel:
    
    def test_user_creation(self, db_session, sample_user_data):
        """Test basic user creation"""
        user = User(**sample_user_data)
        db_session.session.add(user)
        db_session.session.commit()
        
        assert user.id is not None
        assert user.email == sample_user_data['email']
        assert user.first_name == sample_user_data['first_name']
        assert user.last_name == sample_user_data['last_name']
        assert user.is_active is True
        assert user.is_verified is False
        assert user.login_count == 0
    
    def test_password_hashing(self, db_session):
        """Test password hashing and verification"""
        user = User(email='test@example.com', password='testpass123')
        
        # Password should be hashed
        assert user.password_hash != 'testpass123'
        assert len(user.password_hash) > 50  # bcrypt hashes are long
        
        # Should verify correct password
        assert user.check_password('testpass123') is True
        
        # Should reject incorrect password
        assert user.check_password('wrongpass') is False
    
    def test_user_factory(self, db_session):
        """Test user factory creation"""
        user = UserFactory()
        
        assert user.id is not None
        assert '@infrawatch.com' in user.email
        assert user.first_name is not None
        assert user.last_name is not None
        assert user.is_active is True
        assert user.check_password('testpass123') is True
    
    def test_inactive_user_factory(self, db_session):
        """Test inactive user factory"""
        user = UserFactory(is_active=False)
        
        assert user.is_active is False
        assert user.is_verified is True  # Still verified, just inactive
    
    def test_login_update(self, db_session):
        """Test login count and timestamp update"""
        user = UserFactory()
        initial_count = user.login_count
        initial_login = user.last_login
        
        user.update_login()
        
        assert user.login_count == initial_count + 1
        assert user.last_login != initial_login
    
    def test_user_to_dict(self, db_session):
        """Test user serialization"""
        user = UserFactory()
        user_dict = user.to_dict()
        
        assert 'id' in user_dict
        assert 'email' in user_dict
        assert 'password_hash' not in user_dict  # Should not expose password
        assert 'is_active' in user_dict
        assert 'created_at' in user_dict
    
    def test_user_repr(self, db_session):
        """Test user string representation"""
        user = UserFactory(email='test@example.com')
        assert str(user) == '<User test@example.com>'
