import pytest
from app import create_app, db
from app.models.user import User

@pytest.fixture(scope='session')
def app():
    """Create application for testing"""
    app = create_app('testing')
    return app

@pytest.fixture(scope='function')
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture(scope='function')
def app_context(app):
    """Create application context"""
    with app.app_context():
        yield app

@pytest.fixture(scope='function')
def db_session(app_context):
    """Create database session for testing"""
    db.create_all()
    yield db
    db.session.remove()
    db.drop_all()

@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        'email': 'test@infrawatch.com',
        'password': 'TestPass123!',
        'first_name': 'Test',
        'last_name': 'User'
    }
