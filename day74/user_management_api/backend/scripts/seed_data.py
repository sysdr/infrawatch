import asyncio
from faker import Faker
from sqlalchemy import select, func
from app.core.database import AsyncSessionLocal
from app.models.user import User, UserStatus
from app.models.team import Team, TeamMember, TeamRole
from app.models.permission import Permission, UserPermission
from app.models.activity import Activity
from passlib.context import CryptContext

fake = Faker()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def seed_database():
    try:
        async with AsyncSessionLocal() as session:
            # Check if data already exists
            existing_permissions = await session.execute(select(func.count(Permission.id)))
            if existing_permissions.scalar() > 0:
                print("Database already has data. Skipping seed.")
                return
            
            # Create permissions
            permissions = []
            for resource in ['users', 'teams', 'reports']:
                for action in ['read', 'write', 'delete']:
                    perm = Permission(
                        name=f"{resource}:{action}",
                        resource=resource,
                        action=action,
                        description=f"Permission to {action} {resource}"
                    )
                    session.add(perm)
                    permissions.append(perm)
            
            await session.commit()
            
            # Create users
            users = []
            for i in range(20):
                user = User(
                    email=fake.email(),
                    username=fake.user_name() + str(i),
                    full_name=fake.name(),
                    hashed_password=pwd_context.hash("password123"),
                    status=UserStatus.ACTIVE,
                    is_active=True,
                    email_verified=True
                )
                session.add(user)
                users.append(user)
            
            await session.commit()
            
            # Create teams
            teams = []
            for i in range(5):
                team = Team(
                    name=f"{fake.company()} Team",
                    description=fake.catch_phrase()
                )
                session.add(team)
                teams.append(team)
            
            await session.commit()
            
            # Add team members
            for team in teams:
                for user in users[:4]:
                    member = TeamMember(
                        team_id=team.id,
                        user_id=user.id,
                        role=TeamRole.MEMBER
                    )
                    session.add(member)
            
            # Assign permissions
            for user in users[:10]:
                for perm in permissions[:3]:
                    user_perm = UserPermission(
                        user_id=user.id,
                        permission_id=perm.id
                    )
                    session.add(user_perm)
            
            # Create activities
            for user in users[:10]:
                for _ in range(5):
                    activity = Activity(
                        user_id=user.id,
                        action=fake.random_element(['login', 'create_user', 'update_team', 'assign_permission']),
                        resource_type=fake.random_element(['user', 'team', 'permission']),
                        resource_id=str(fake.uuid4()),
                        details={'ip': fake.ipv4()}
                    )
                    session.add(activity)
            
            await session.commit()
            print("Database seeded successfully!")
    except Exception as e:
        print(f"Error seeding database: {e}")
        # Continue anyway - data might already exist

if __name__ == "__main__":
    asyncio.run(seed_database())
