#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from src.database.config import get_engine, Base, SessionLocal
from src.models.user import User, Role, Permission
from src.auth.utils import get_password_hash

def init_database():
    """Initialize database with default roles and permissions"""
    print("🔧 Initializing database...")
    
    # Create all tables
    Base.metadata.create_all(bind=get_engine())
    
    db = SessionLocal()
    try:
        # Create default permissions
        permissions_data = [
            {"name": "read_logs", "description": "Read log entries", "resource": "logs", "action": "read"},
            {"name": "write_logs", "description": "Write log entries", "resource": "logs", "action": "write"},
            {"name": "delete_logs", "description": "Delete log entries", "resource": "logs", "action": "delete"},
            {"name": "search_logs", "description": "Search log entries", "resource": "logs", "action": "search"},
            {"name": "export_logs", "description": "Export log entries", "resource": "logs", "action": "export"},
            {"name": "view_analytics", "description": "View analytics dashboard", "resource": "analytics", "action": "view"},
            {"name": "manage_users", "description": "Manage user accounts", "resource": "users", "action": "manage"},
            {"name": "manage_roles", "description": "Manage roles", "resource": "roles", "action": "manage"},
            {"name": "manage_permissions", "description": "Manage permissions", "resource": "permissions", "action": "manage"},
            {"name": "manage_system", "description": "Manage system configuration", "resource": "system", "action": "manage"},
        ]
        
        permissions = []
        for perm_data in permissions_data:
            existing = db.query(Permission).filter(Permission.name == perm_data["name"]).first()
            if not existing:
                permission = Permission(**perm_data)
                db.add(permission)
                permissions.append(permission)
                print(f"  ✅ Created permission: {perm_data['name']}")
            else:
                permissions.append(existing)
        
        db.commit()
        
        # Create default roles
        roles_data = [
            {
                "name": "admin", 
                "description": "System administrator with full access",
                "permissions": [p for p in permissions if p.name in [
                    "read_logs", "write_logs", "delete_logs", "search_logs", "export_logs",
                    "view_analytics", "manage_users", "manage_roles", "manage_permissions", "manage_system"
                ]]
            },
            {
                "name": "log_analyst",
                "description": "Log analyst with read and search access",
                "permissions": [p for p in permissions if p.name in [
                    "read_logs", "search_logs", "export_logs", "view_analytics"
                ]]
            },
            {
                "name": "log_writer",
                "description": "Service account for writing logs",
                "permissions": [p for p in permissions if p.name in ["write_logs"]]
            },
            {
                "name": "viewer",
                "description": "Read-only access to logs",
                "permissions": [p for p in permissions if p.name in ["read_logs", "view_analytics"]]
            }
        ]
        
        roles = []
        for role_data in roles_data:
            existing = db.query(Role).filter(Role.name == role_data["name"]).first()
            if not existing:
                role = Role(name=role_data["name"], description=role_data["description"])
                role.permissions = role_data["permissions"]
                db.add(role)
                roles.append(role)
                print(f"  ✅ Created role: {role_data['name']} with {len(role_data['permissions'])} permissions")
            else:
                roles.append(existing)
        
        db.commit()
        
        # Create default admin user
        admin_exists = db.query(User).filter(User.username == "admin").first()
        if not admin_exists:
            admin_role = db.query(Role).filter(Role.name == "admin").first()
            admin_user = User(
                email="admin@rbac-system.com",
                username="admin",
                hashed_password=get_password_hash("admin123"),
                is_active=True,
                is_verified=True
            )
            admin_user.roles = [admin_role]
            db.add(admin_user)
            db.commit()
            print("  ✅ Created default admin user (username: admin, password: admin123)")
        
        print("✅ Database initialized successfully!")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
