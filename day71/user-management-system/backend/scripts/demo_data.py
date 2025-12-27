#!/usr/bin/env python3
"""
Demo script to generate test data for the User Management System
This script creates a test user and generates various activities
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.user import User, UserStatus
from app.models.profile import UserProfile
from app.models.preference import UserPreference
from app.models.activity import UserActivity, ActivityType
from app.core.security import get_password_hash
from app.services.activity_service import activity_service

def create_demo_user(db: Session):
    """Create a demo user if it doesn't exist"""
    email = "demo@example.com"
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        print(f"Creating demo user: {email}")
        user = User(
            email=email,
            username="demo",
            hashed_password=get_password_hash("demo123456"),
            status=UserStatus.ACTIVE,
            is_active=True,
            is_verified=True
        )
        db.add(user)
        db.flush()
        
        # Create profile
        profile = UserProfile(
            user_id=user.id,
            display_name="Demo User",
            first_name="Demo",
            last_name="User",
            bio="This is a demo user for testing",
            job_title="Software Engineer",
            department="Engineering",
            company="Demo Corp",
            location="San Francisco, CA"
        )
        db.add(profile)
        
        # Create preferences
        preferences = UserPreference(
            user_id=user.id,
            preferences={
                "theme": "light",
                "language": "en",
                "notifications": {"email": True, "push": True}
            }
        )
        db.add(preferences)
        
        db.commit()
        db.refresh(user)
        print(f"✓ Demo user created with ID: {user.id}")
    else:
        print(f"Demo user already exists: {email}")
    
    return user

def generate_activities(db: Session, user_id: int, count: int = 50):
    """Generate random activities for the user"""
    print(f"Generating {count} activities...")
    
    activity_types = [
        ("auth.login", "User logged in"),
        ("auth.logout", "User logged out"),
        ("profile.updated", "Profile information updated"),
        ("dashboard.viewed", "Dashboard viewed"),
        ("dashboard.created", "Dashboard created"),
        ("preference.updated", "User preferences updated"),
        ("dashboard.updated", "Dashboard updated"),
    ]
    
    base_time = datetime.utcnow()
    
    for i in range(count):
        action, description = random.choice(activity_types)
        activity_time = base_time - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
        
        # Create activity directly (since we're in sync context)
        activity = UserActivity(
            user_id=user_id,
            action=action,
            description=description,
            activity_metadata={"demo": True, "index": i},
            ip_address=f"192.168.1.{random.randint(1, 255)}",
            user_agent="Mozilla/5.0 (Demo Browser)",
            created_at=activity_time
        )
        db.add(activity)
        if (i + 1) % 10 == 0:
            db.commit()
    
    db.commit()
    print(f"✓ Generated {count} activities")

def main():
    print("=" * 50)
    print("User Management System - Demo Data Generator")
    print("=" * 50)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Create demo user
        user = create_demo_user(db)
        
        # Generate activities
        generate_activities(db, user.id, count=50)
        
        # Get activity count
        activity_count = db.query(UserActivity).filter(UserActivity.user_id == user.id).count()
        print(f"\n✓ Demo data generation complete!")
        print(f"  User ID: {user.id}")
        print(f"  Email: {user.email}")
        print(f"  Password: demo123456")
        print(f"  Total Activities: {activity_count}")
        print("\nYou can now login with:")
        print(f"  Email: {user.email}")
        print(f"  Password: demo123456")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()

