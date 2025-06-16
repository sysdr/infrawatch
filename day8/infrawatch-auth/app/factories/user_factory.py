import factory
from factory.alchemy import SQLAlchemyModelFactory
from app import db
from app.models.user import User

class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    
    email = factory.Sequence(lambda n: f'user{n}@infrawatch.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True
    is_verified = True
    
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override _create to ensure password is set before commit"""
        password = kwargs.pop('password', 'testpass123')
        obj = model_class(**kwargs)
        obj.set_password(password)
        return cls._save(model_class, db.session, args, {'password_hash': obj.password_hash, **kwargs})

class InactiveUserFactory(UserFactory):
    is_active = False
    is_verified = False

class AdminUserFactory(UserFactory):
    email = factory.Sequence(lambda n: f'admin{n}@infrawatch.com')
    first_name = 'Admin'
    last_name = factory.Faker('last_name')
