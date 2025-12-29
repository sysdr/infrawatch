#!/usr/bin/env python3
"""
Demo data generation script for Team Management System
Creates sample data to populate the dashboard with non-zero metrics
"""
import asyncio
import sys
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.models.team import (
    Organization, Team, Role, TeamMember, TeamActivity, User
)
from app.services.team_service import TeamService
from app.schemas.team import TeamCreate
from app.config import settings
from datetime import datetime, timedelta
import random

engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def create_demo_data():
    """Create demo data for the dashboard"""
    async with async_session_maker() as session:
        try:
            # Create users
            print("Creating users...")
            users = []
            for i in range(1, 6):
                user = User(
                    email=f"user{i}@demo.com",
                    username=f"user{i}",
                    full_name=f"Demo User {i}",
                    hashed_password="demo",
                    is_active=True
                )
                session.add(user)
                users.append(user)
            await session.flush()
            print(f"Created {len(users)} users")

            # Create organization
            print("Creating organization...")
            org = Organization(
                name="Demo Organization",
                slug="demo-org",
                settings={}
            )
            session.add(org)
            await session.flush()
            print(f"Created organization: {org.name} (ID: {org.id})")

            # Create roles
            print("Creating roles...")
            admin_role = Role(
                name="Admin",
                description="Administrator role",
                permissions=["all"],
                is_system_role=True
            )
            member_role = Role(
                name="Member",
                description="Team member role",
                permissions=["read", "write"],
                is_system_role=False
            )
            session.add(admin_role)
            session.add(member_role)
            await session.flush()
            print(f"Created roles: Admin (ID: {admin_role.id}), Member (ID: {member_role.id})")

            # Create team
            print("Creating team...")
            service = TeamService(session)
            team_data = TeamCreate(
                organization_id=org.id,
                name="Development Team",
                description="Main development team",
                parent_team_id=None,
                metadata={}
            )
            team = await service.create_team(team_data, creator_id=users[0].id)
            print(f"Created team: {team.name} (ID: {team.id})")

            # Add members to team
            print("Adding team members...")
            for i, user in enumerate(users[1:], 1):
                role_id = admin_role.id if i == 1 else member_role.id
                member = await service.add_team_member(
                    team.id,
                    user.id,
                    role_id,
                    inviter_id=users[0].id
                )
                print(f"Added member: User {user.id} to team {team.id}")

            # Create activities for dashboard metrics
            print("Creating activities...")
            activity_types = [
                "task_created", "task_completed", "comment_added",
                "file_uploaded", "meeting_scheduled", "code_review"
            ]
            
            # Create activities for today
            today = datetime.utcnow()
            for _ in range(15):
                activity = TeamActivity(
                    team_id=team.id,
                    user_id=random.choice(users).id,
                    activity_type=random.choice(activity_types),
                    description=f"Demo activity: {random.choice(activity_types)}",
                    activity_metadata={"demo": True},
                    created_at=today - timedelta(hours=random.randint(0, 23))
                )
                session.add(activity)

            # Create activities for this week
            for _ in range(30):
                activity = TeamActivity(
                    team_id=team.id,
                    user_id=random.choice(users).id,
                    activity_type=random.choice(activity_types),
                    description=f"Demo activity: {random.choice(activity_types)}",
                    activity_metadata={"demo": True},
                    created_at=today - timedelta(days=random.randint(1, 6))
                )
                session.add(activity)

            # Create older activities
            for _ in range(20):
                activity = TeamActivity(
                    team_id=team.id,
                    user_id=random.choice(users).id,
                    activity_type=random.choice(activity_types),
                    description=f"Demo activity: {random.choice(activity_types)}",
                    activity_metadata={"demo": True},
                    created_at=today - timedelta(days=random.randint(7, 30))
                )
                session.add(activity)

            await session.commit()
            print(f"Created {65} activities")
            print("\n=== Demo Data Created Successfully ===")
            print(f"Organization ID: {org.id}")
            print(f"Team ID: {team.id}")
            print(f"Users: {[u.id for u in users]}")
            print(f"Roles: Admin={admin_role.id}, Member={member_role.id}")
            print(f"\nDashboard should now show:")
            print(f"  - Total Members: {len(users)}")
            print(f"  - Active Today: ~{min(15, len(users))}")
            print(f"  - Active This Week: ~{min(45, len(users))}")
            print(f"  - Total Activities: 65")
            
            return team.id

        except Exception as e:
            await session.rollback()
            print(f"Error creating demo data: {e}", file=sys.stderr)
            raise

async def main():
    """Main entry point"""
    try:
        team_id = await create_demo_data()
        print(f"\nTo view dashboard, use team ID: {team_id}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())

