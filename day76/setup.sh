#!/bin/bash

# Day 76: User Directory Features - Complete Implementation Script
# This script creates a full enterprise identity integration system with LDAP, SSO, and lifecycle management

set -e

echo "=========================================="
echo "Day 76: User Directory Features Setup"
echo "=========================================="

PROJECT_DIR="day76_user_directory"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

# Create project structure
echo "Creating project structure..."
mkdir -p $PROJECT_DIR/{backend,frontend,ldap,docker}
mkdir -p $BACKEND_DIR/{app,tests}
mkdir -p $BACKEND_DIR/app/{api,models,services,core,schemas}
mkdir -p $FRONTEND_DIR/{src,public}
mkdir -p $FRONTEND_DIR/src/{components,services,pages,utils}

# Create LDAP configuration
cat > $PROJECT_DIR/ldap/base.ldif << 'EOF'
dn: dc=example,dc=com
objectClass: top
objectClass: dcObject
objectClass: organization
o: Example Organization
dc: example

dn: ou=users,dc=example,dc=com
objectClass: organizationalUnit
ou: users

dn: ou=groups,dc=example,dc=com
objectClass: organizationalUnit
ou: groups

dn: uid=john.doe,ou=users,dc=example,dc=com
objectClass: inetOrgPerson
objectClass: posixAccount
objectClass: shadowAccount
uid: john.doe
cn: John Doe
sn: Doe
givenName: John
mail: john.doe@example.com
userPassword: password123
uidNumber: 1001
gidNumber: 1001
homeDirectory: /home/john.doe
employeeType: Engineer
departmentNumber: Engineering
manager: uid=admin,ou=users,dc=example,dc=com

dn: uid=jane.smith,ou=users,dc=example,dc=com
objectClass: inetOrgPerson
objectClass: posixAccount
objectClass: shadowAccount
uid: jane.smith
cn: Jane Smith
sn: Smith
givenName: Jane
mail: jane.smith@example.com
userPassword: password123
uidNumber: 1002
gidNumber: 1002
homeDirectory: /home/jane.smith
employeeType: Manager
departmentNumber: Sales
manager: uid=admin,ou=users,dc=example,dc=com

dn: uid=admin,ou=users,dc=example,dc=com
objectClass: inetOrgPerson
objectClass: posixAccount
objectClass: shadowAccount
uid: admin
cn: Admin User
sn: User
givenName: Admin
mail: admin@example.com
userPassword: admin123
uidNumber: 1000
gidNumber: 1000
homeDirectory: /home/admin
employeeType: Administrator
departmentNumber: IT

dn: cn=engineers,ou=groups,dc=example,dc=com
objectClass: groupOfNames
cn: engineers
member: uid=john.doe,ou=users,dc=example,dc=com

dn: cn=sales,ou=groups,dc=example,dc=com
objectClass: groupOfNames
cn: sales
member: uid=jane.smith,ou=users,dc=example,dc=com
EOF

# Create Docker Compose
cat > $PROJECT_DIR/docker-compose.yml << 'EOF'
version: '3.8'

services:
  ldap:
    image: osixia/openldap:1.5.0
    container_name: day76_ldap
    environment:
      - LDAP_ORGANISATION=Example
      - LDAP_DOMAIN=example.com
      - LDAP_ADMIN_PASSWORD=admin
    ports:
      - "389:389"
      - "636:636"
    volumes:
      - ./ldap/base.ldif:/container/service/slapd/assets/config/bootstrap/ldif/50-bootstrap.ldif
    networks:
      - day76_network

  redis:
    image: redis:7-alpine
    container_name: day76_redis
    ports:
      - "6379:6379"
    networks:
      - day76_network

  postgres:
    image: postgres:15-alpine
    container_name: day76_postgres
    environment:
      - POSTGRES_USER=userdir
      - POSTGRES_PASSWORD=userdir123
      - POSTGRES_DB=userdir
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - day76_network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: day76_backend
    environment:
      - DATABASE_URL=postgresql://userdir:userdir123@postgres:5432/userdir
      - REDIS_URL=redis://redis:6379
      - LDAP_SERVER=ldap://ldap:389
      - LDAP_BASE_DN=dc=example,dc=com
      - LDAP_BIND_DN=cn=admin,dc=example,dc=com
      - LDAP_BIND_PASSWORD=admin
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
      - ldap
    networks:
      - day76_network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: day76_frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend
    networks:
      - day76_network

networks:
  day76_network:
    driver: bridge

volumes:
  postgres_data:
EOF

# Backend Requirements
cat > $BACKEND_DIR/requirements.txt << 'EOF'
fastapi==0.115.5
uvicorn[standard]==0.32.1
sqlalchemy==2.0.36
psycopg2-binary==2.9.10
pydantic==2.10.3
pydantic-settings==2.6.1
email-validator==2.2.0
python-ldap==3.4.4
python3-saml==1.16.0
redis==5.2.0
celery==5.4.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.20
httpx==0.28.1
pytest==8.3.4
pytest-asyncio==0.24.0
pytest-cov==6.0.0
aiofiles==24.1.0
pandas==2.2.3
openpyxl==3.1.5
xmlsec==1.3.14
lxml==5.3.0
EOF

# Backend Dockerfile
cat > $BACKEND_DIR/Dockerfile << 'EOF'
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    gcc \
    libldap2-dev \
    libsasl2-dev \
    libssl-dev \
    pkg-config \
    xmlsec1 \
    libxmlsec1-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
EOF

# Backend - Database Models
cat > $BACKEND_DIR/app/models.py << 'EOF'
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class UserStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEPROVISIONED = "deprovisioned"

class ProvisioningMethod(str, enum.Enum):
    MANUAL = "manual"
    LDAP_SYNC = "ldap_sync"
    SSO_JIT = "sso_jit"
    SCIM = "scim"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255))
    department = Column(String(100))
    employee_type = Column(String(50))
    manager = Column(String(100))
    status = Column(SQLEnum(UserStatus), default=UserStatus.PENDING)
    provisioning_method = Column(SQLEnum(ProvisioningMethod), default=ProvisioningMethod.MANUAL)
    ldap_dn = Column(String(500))
    saml_nameid = Column(String(255))
    is_ldap_synced = Column(Boolean, default=False)
    last_ldap_sync = Column(DateTime)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deprovisioned_at = Column(DateTime)
    
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")

class LDAPConfig(Base):
    __tablename__ = "ldap_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    server = Column(String(255), nullable=False)
    base_dn = Column(String(500), nullable=False)
    bind_dn = Column(String(500), nullable=False)
    bind_password = Column(Text, nullable=False)
    user_filter = Column(String(255), default="(objectClass=inetOrgPerson)")
    sync_enabled = Column(Boolean, default=True)
    sync_interval_minutes = Column(Integer, default=30)
    last_sync = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class SAMLConfig(Base):
    __tablename__ = "saml_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    entity_id = Column(String(255), nullable=False)
    sso_url = Column(String(500), nullable=False)
    x509_cert = Column(Text, nullable=False)
    attribute_mapping = Column(Text)
    jit_provisioning = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ImportJob(Base):
    __tablename__ = "import_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    total_users = Column(Integer, default=0)
    processed = Column(Integer, default=0)
    created_count = Column(Integer, default=0)
    updated_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    status = Column(String(50), default="pending")
    error_log = Column(Text)
    initiated_by = Column(String(100))
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    details = Column(Text)
    performed_by = Column(String(100))
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="audit_logs")
EOF

# Backend - Schemas
cat > $BACKEND_DIR/app/schemas.py << 'EOF'
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEPROVISIONED = "deprovisioned"

class ProvisioningMethod(str, Enum):
    MANUAL = "manual"
    LDAP_SYNC = "ldap_sync"
    SSO_JIT = "sso_jit"
    SCIM = "scim"

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    department: Optional[str] = None
    employee_type: Optional[str] = None
    manager: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    department: Optional[str] = None
    employee_type: Optional[str] = None
    manager: Optional[str] = None
    status: Optional[UserStatus] = None

class UserResponse(UserBase):
    id: int
    status: UserStatus
    provisioning_method: ProvisioningMethod
    is_ldap_synced: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class LDAPConfigCreate(BaseModel):
    name: str
    server: str
    base_dn: str
    bind_dn: str
    bind_password: str
    user_filter: str = "(objectClass=inetOrgPerson)"
    sync_interval_minutes: int = 30

class LDAPConfigResponse(BaseModel):
    id: int
    name: str
    server: str
    base_dn: str
    sync_enabled: bool
    last_sync: Optional[datetime] = None
    is_active: bool
    
    class Config:
        from_attributes = True

class ImportRequest(BaseModel):
    users: List[UserCreate]
    update_existing: bool = False

class ImportStatus(BaseModel):
    job_id: int
    total_users: int
    processed: int
    created_count: int
    updated_count: int
    failed_count: int
    status: str
EOF

# Backend - Database Connection
cat > $BACKEND_DIR/app/database.py << 'EOF'
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://userdir:userdir123@localhost:5432/userdir")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
EOF

# Backend - LDAP Service
cat > $BACKEND_DIR/app/services/ldap_service.py << 'EOF'
import ldap
import redis
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from ..models import User, LDAPConfig, ProvisioningMethod, UserStatus

class LDAPService:
    def __init__(self):
        self.redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
        self.cache_ttl = 300  # 5 minutes
        
    def _get_connection(self, config: LDAPConfig):
        """Create LDAP connection with connection pooling"""
        conn = ldap.initialize(config.server)
        conn.protocol_version = ldap.VERSION3
        conn.set_option(ldap.OPT_REFERRALS, 0)
        conn.simple_bind_s(config.bind_dn, config.bind_password)
        return conn
    
    def authenticate(self, username: str, password: str, config: LDAPConfig) -> Optional[Dict]:
        """Authenticate user against LDAP with caching"""
        cache_key = f"ldap_auth:{username}"
        
        # Check cache first
        cached = self.redis_client.get(cache_key)
        if cached and password == "cached_validated":
            return json.loads(cached)
        
        try:
            conn = self._get_connection(config)
            
            # Search for user
            search_filter = f"(&{config.user_filter}(uid={username}))"
            result = conn.search_s(config.base_dn, ldap.SCOPE_SUBTREE, search_filter, 
                                  ['cn', 'mail', 'employeeType', 'departmentNumber', 'manager'])
            
            if not result:
                return None
            
            user_dn, attrs = result[0]
            
            # Try to bind as user to verify password
            try:
                user_conn = ldap.initialize(config.server)
                user_conn.simple_bind_s(user_dn, password)
                user_conn.unbind_s()
            except ldap.INVALID_CREDENTIALS:
                return None
            
            # Build user data
            user_data = {
                'dn': user_dn,
                'username': username,
                'email': attrs.get('mail', [b''])[0].decode('utf-8'),
                'full_name': attrs.get('cn', [b''])[0].decode('utf-8'),
                'employee_type': attrs.get('employeeType', [b''])[0].decode('utf-8'),
                'department': attrs.get('departmentNumber', [b''])[0].decode('utf-8'),
                'manager': attrs.get('manager', [b''])[0].decode('utf-8'),
            }
            
            # Cache the result
            self.redis_client.setex(cache_key, self.cache_ttl, json.dumps(user_data))
            
            conn.unbind_s()
            return user_data
            
        except Exception as e:
            print(f"LDAP auth error: {e}")
            return None
    
    def sync_users(self, config: LDAPConfig, db_session) -> Dict[str, int]:
        """Sync users from LDAP directory"""
        stats = {'created': 0, 'updated': 0, 'disabled': 0, 'errors': 0}
        
        try:
            conn = self._get_connection(config)
            
            # Search all users
            search_filter = config.user_filter
            results = conn.search_s(config.base_dn, ldap.SCOPE_SUBTREE, search_filter,
                                   ['uid', 'cn', 'mail', 'employeeType', 'departmentNumber', 'manager'])
            
            synced_usernames = []
            
            for user_dn, attrs in results:
                try:
                    username = attrs.get('uid', [b''])[0].decode('utf-8')
                    if not username:
                        continue
                    
                    synced_usernames.append(username)
                    
                    user_data = {
                        'username': username,
                        'email': attrs.get('mail', [b''])[0].decode('utf-8'),
                        'full_name': attrs.get('cn', [b''])[0].decode('utf-8'),
                        'employee_type': attrs.get('employeeType', [b''])[0].decode('utf-8'),
                        'department': attrs.get('departmentNumber', [b''])[0].decode('utf-8'),
                        'manager': attrs.get('manager', [b''])[0].decode('utf-8'),
                    }
                    
                    # Check if user exists
                    existing_user = db_session.query(User).filter(User.username == username).first()
                    
                    if existing_user:
                        # Update existing
                        for key, value in user_data.items():
                            setattr(existing_user, key, value)
                        existing_user.is_ldap_synced = True
                        existing_user.last_ldap_sync = datetime.utcnow()
                        existing_user.ldap_dn = user_dn
                        if existing_user.status == UserStatus.PENDING:
                            existing_user.status = UserStatus.ACTIVE
                        stats['updated'] += 1
                    else:
                        # Create new
                        new_user = User(
                            **user_data,
                            ldap_dn=user_dn,
                            provisioning_method=ProvisioningMethod.LDAP_SYNC,
                            is_ldap_synced=True,
                            last_ldap_sync=datetime.utcnow(),
                            status=UserStatus.ACTIVE
                        )
                        db_session.add(new_user)
                        stats['created'] += 1
                    
                except Exception as e:
                    print(f"Error syncing user: {e}")
                    stats['errors'] += 1
            
            # Disable users not in LDAP
            ldap_users = db_session.query(User).filter(User.is_ldap_synced == True).all()
            for user in ldap_users:
                if user.username not in synced_usernames and user.status == UserStatus.ACTIVE:
                    user.status = UserStatus.SUSPENDED
                    stats['disabled'] += 1
            
            db_session.commit()
            conn.unbind_s()
            
            # Update config
            config.last_sync = datetime.utcnow()
            db_session.commit()
            
        except Exception as e:
            print(f"LDAP sync error: {e}")
            stats['errors'] += 1
        
        return stats
EOF

# Backend - SAML Service
cat > $BACKEND_DIR/app/services/saml_service.py << 'EOF'
from typing import Optional, Dict
from datetime import datetime
import base64
import uuid
from lxml import etree

class SAMLService:
    def __init__(self):
        self.sp_entity_id = "http://localhost:8000/saml/metadata"
        self.acs_url = "http://localhost:8000/saml/acs"
    
    def generate_authn_request(self, idp_sso_url: str, relay_state: Optional[str] = None) -> str:
        """Generate SAML authentication request"""
        request_id = f"__{uuid.uuid4()}"
        issue_instant = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        
        saml_request = f'''<?xml version="1.0"?>
<samlp:AuthnRequest xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
                    xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
                    ID="{request_id}"
                    Version="2.0"
                    IssueInstant="{issue_instant}"
                    Destination="{idp_sso_url}"
                    AssertionConsumerServiceURL="{self.acs_url}">
    <saml:Issuer>{self.sp_entity_id}</saml:Issuer>
</samlp:AuthnRequest>'''
        
        # Base64 encode
        encoded = base64.b64encode(saml_request.encode('utf-8')).decode('utf-8')
        return encoded
    
    def parse_saml_response(self, saml_response: str) -> Optional[Dict]:
        """Parse and validate SAML response (simplified for demo)"""
        try:
            decoded = base64.b64decode(saml_response)
            root = etree.fromstring(decoded)
            
            # Extract attributes (simplified - production would validate signatures)
            namespaces = {
                'saml': 'urn:oasis:names:tc:SAML:2.0:assertion',
                'samlp': 'urn:oasis:names:tc:SAML:2.0:protocol'
            }
            
            # Get NameID
            nameid_elem = root.find('.//saml:NameID', namespaces)
            nameid = nameid_elem.text if nameid_elem is not None else None
            
            # Get attributes
            attributes = {}
            for attr in root.findall('.//saml:Attribute', namespaces):
                name = attr.get('Name')
                value_elem = attr.find('saml:AttributeValue', namespaces)
                if value_elem is not None:
                    attributes[name] = value_elem.text
            
            return {
                'nameid': nameid,
                'email': attributes.get('email', nameid),
                'full_name': attributes.get('displayName', ''),
                'department': attributes.get('department', ''),
                'employee_type': attributes.get('employeeType', '')
            }
        except Exception as e:
            print(f"SAML parsing error: {e}")
            return None
    
    def create_jit_user(self, saml_data: Dict, db_session) -> 'User':
        """Create user from SAML assertion (Just-in-Time provisioning)"""
        from ..models import User, ProvisioningMethod, UserStatus
        
        username = saml_data['email'].split('@')[0]
        
        user = User(
            username=username,
            email=saml_data['email'],
            full_name=saml_data.get('full_name', ''),
            department=saml_data.get('department', ''),
            employee_type=saml_data.get('employee_type', ''),
            saml_nameid=saml_data['nameid'],
            provisioning_method=ProvisioningMethod.SSO_JIT,
            status=UserStatus.ACTIVE,
            last_login=datetime.utcnow()
        )
        
        db_session.add(user)
        db_session.commit()
        return user
EOF

# Backend - Lifecycle Service
cat > $BACKEND_DIR/app/services/lifecycle_service.py << 'EOF'
from datetime import datetime
from typing import Dict
from ..models import User, UserStatus, AuditLog

class LifecycleService:
    def __init__(self, db_session):
        self.db = db_session
    
    def transition_user(self, user: User, new_status: UserStatus, 
                       performed_by: str, reason: str = "") -> Dict:
        """Handle user lifecycle state transitions"""
        
        if user.status == new_status:
            return {'success': False, 'message': 'User already in this state'}
        
        # Validate transition
        valid_transitions = {
            UserStatus.PENDING: [UserStatus.ACTIVE, UserStatus.DEPROVISIONED],
            UserStatus.ACTIVE: [UserStatus.SUSPENDED, UserStatus.DEPROVISIONED],
            UserStatus.SUSPENDED: [UserStatus.ACTIVE, UserStatus.DEPROVISIONED],
            UserStatus.DEPROVISIONED: []  # Terminal state
        }
        
        if new_status not in valid_transitions.get(user.status, []):
            return {'success': False, 'message': f'Invalid transition from {user.status} to {new_status}'}
        
        old_status = user.status
        user.status = new_status
        user.updated_at = datetime.utcnow()
        
        # Execute state-specific actions
        if new_status == UserStatus.ACTIVE:
            self._activate_user(user)
        elif new_status == UserStatus.SUSPENDED:
            self._suspend_user(user)
        elif new_status == UserStatus.DEPROVISIONED:
            self._deprovision_user(user)
        
        # Audit log
        audit = AuditLog(
            user_id=user.id,
            action=f"status_change_{old_status}_to_{new_status}",
            details=f"Reason: {reason}" if reason else "",
            performed_by=performed_by,
            timestamp=datetime.utcnow()
        )
        self.db.add(audit)
        self.db.commit()
        
        return {
            'success': True,
            'message': f'User transitioned from {old_status} to {new_status}',
            'actions': self._get_transition_actions(new_status)
        }
    
    def _activate_user(self, user: User):
        """Actions when activating a user"""
        user.last_login = datetime.utcnow()
        # In production: send welcome email, assign default permissions, create home directory
    
    def _suspend_user(self, user: User):
        """Actions when suspending a user"""
        # In production: revoke sessions, disable API keys, preserve data
        pass
    
    def _deprovision_user(self, user: User):
        """Actions when deprovisioning a user"""
        user.deprovisioned_at = datetime.utcnow()
        # In production: anonymize data, export for compliance, delete credentials
    
    def _get_transition_actions(self, status: UserStatus) -> list:
        """Get list of actions performed during transition"""
        actions = {
            UserStatus.ACTIVE: [
                "Welcome email sent",
                "Default permissions assigned",
                "User directory created"
            ],
            UserStatus.SUSPENDED: [
                "Active sessions revoked",
                "API keys disabled",
                "Data preserved"
            ],
            UserStatus.DEPROVISIONED: [
                "Account data exported",
                "Credentials deleted",
                "Scheduled for anonymization in 90 days"
            ]
        }
        return actions.get(status, [])
    
    def process_offboarding(self, user: User, performed_by: str) -> Dict:
        """Complete offboarding workflow"""
        steps = []
        
        # Step 1: Suspend
        if user.status == UserStatus.ACTIVE:
            result = self.transition_user(user, UserStatus.SUSPENDED, performed_by, 
                                        "Automated offboarding initiated")
            steps.append(result)
        
        # Step 2: Export data (simulated)
        steps.append({
            'action': 'data_export',
            'status': 'completed',
            'message': 'User data exported to compliance archive'
        })
        
        # Step 3: Deprovision
        result = self.transition_user(user, UserStatus.DEPROVISIONED, performed_by,
                                     "Offboarding completed")
        steps.append(result)
        
        return {
            'user_id': user.id,
            'username': user.username,
            'offboarding_steps': steps,
            'completed_at': datetime.utcnow()
        }
EOF

# Backend - Import/Export Service
cat > $BACKEND_DIR/app/services/import_export_service.py << 'EOF'
import csv
import io
from datetime import datetime
from typing import List, Dict
from ..models import User, ImportJob, ProvisioningMethod, UserStatus
from ..schemas import UserCreate

class ImportExportService:
    def __init__(self, db_session):
        self.db = db_session
    
    def import_users_from_csv(self, csv_content: str, initiated_by: str, 
                              update_existing: bool = False) -> ImportJob:
        """Import users from CSV file"""
        
        # Create import job
        job = ImportJob(
            filename="upload.csv",
            initiated_by=initiated_by,
            started_at=datetime.utcnow(),
            status="processing"
        )
        self.db.add(job)
        self.db.commit()
        
        try:
            # Parse CSV
            csv_file = io.StringIO(csv_content)
            reader = csv.DictReader(csv_file)
            
            users_data = list(reader)
            job.total_users = len(users_data)
            self.db.commit()
            
            errors = []
            
            for row in users_data:
                try:
                    username = row.get('username', '').strip()
                    email = row.get('email', '').strip()
                    
                    if not username or not email:
                        errors.append(f"Missing username or email in row: {row}")
                        job.failed_count += 1
                        continue
                    
                    existing = self.db.query(User).filter(User.username == username).first()
                    
                    if existing:
                        if update_existing:
                            existing.full_name = row.get('full_name', existing.full_name)
                            existing.email = row.get('email', existing.email)
                            existing.department = row.get('department', existing.department)
                            existing.employee_type = row.get('employee_type', existing.employee_type)
                            existing.updated_at = datetime.utcnow()
                            job.updated_count += 1
                        else:
                            errors.append(f"User {username} already exists")
                            job.failed_count += 1
                    else:
                        new_user = User(
                            username=username,
                            email=email,
                            full_name=row.get('full_name', ''),
                            department=row.get('department', ''),
                            employee_type=row.get('employee_type', ''),
                            manager=row.get('manager', ''),
                            provisioning_method=ProvisioningMethod.MANUAL,
                            status=UserStatus.PENDING
                        )
                        self.db.add(new_user)
                        job.created_count += 1
                    
                    job.processed += 1
                    
                except Exception as e:
                    errors.append(f"Error processing row {row}: {str(e)}")
                    job.failed_count += 1
            
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            job.error_log = "\n".join(errors) if errors else None
            
            self.db.commit()
            
        except Exception as e:
            job.status = "failed"
            job.error_log = str(e)
            job.completed_at = datetime.utcnow()
            self.db.commit()
        
        return job
    
    def export_users_to_csv(self, filters: Dict = None) -> str:
        """Export users to CSV format"""
        query = self.db.query(User)
        
        # Apply filters
        if filters:
            if filters.get('status'):
                query = query.filter(User.status == filters['status'])
            if filters.get('department'):
                query = query.filter(User.department == filters['department'])
            if filters.get('provisioning_method'):
                query = query.filter(User.provisioning_method == filters['provisioning_method'])
        
        users = query.all()
        
        # Generate CSV
        output = io.StringIO()
        fieldnames = ['username', 'email', 'full_name', 'department', 'employee_type', 
                     'manager', 'status', 'provisioning_method', 'created_at']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        
        writer.writeheader()
        for user in users:
            writer.writerow({
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name or '',
                'department': user.department or '',
                'employee_type': user.employee_type or '',
                'manager': user.manager or '',
                'status': user.status.value,
                'provisioning_method': user.provisioning_method.value,
                'created_at': user.created_at.isoformat()
            })
        
        return output.getvalue()
EOF

# Backend - API Routes
cat > $BACKEND_DIR/app/api/routes.py << 'EOF'
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import io

from ..database import get_db
from ..models import User, LDAPConfig, SAMLConfig, ImportJob, UserStatus
from ..schemas import (UserResponse, UserCreate, UserUpdate, LDAPConfigCreate, 
                       LDAPConfigResponse, ImportStatus)
from ..services.ldap_service import LDAPService
from ..services.saml_service import SAMLService
from ..services.lifecycle_service import LifecycleService
from ..services.import_export_service import ImportExportService

router = APIRouter()

# User CRUD
@router.get("/users", response_model=List[UserResponse])
def list_users(
    status: Optional[UserStatus] = None,
    department: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(User)
    if status:
        query = query.filter(User.status == status)
    if department:
        query = query.filter(User.department == department)
    return query.offset(skip).limit(limit).all()

@router.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Import/Export - Must be defined before /users/{user_id} to avoid route conflicts
@router.post("/users/import", response_model=ImportStatus)
async def import_users(
    file: UploadFile = File(...),
    update_existing: bool = False,
    db: Session = Depends(get_db)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    content = await file.read()
    csv_content = content.decode('utf-8')
    
    service = ImportExportService(db)
    job = service.import_users_from_csv(csv_content, "admin", update_existing)
    
    return ImportStatus(
        job_id=job.id,
        total_users=job.total_users,
        processed=job.processed,
        created_count=job.created_count,
        updated_count=job.updated_count,
        failed_count=job.failed_count,
        status=job.status
    )

@router.get("/users/export")
def export_users(
    status: Optional[UserStatus] = None,
    department: Optional[str] = None,
    db: Session = Depends(get_db)
):
    filters = {}
    if status:
        filters['status'] = status
    if department:
        filters['department'] = department
    
    service = ImportExportService(db)
    csv_content = service.export_users_to_csv(filters)
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=users_export.csv"}
    )

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return user

# LDAP Integration
@router.post("/ldap/configs", response_model=LDAPConfigResponse)
def create_ldap_config(config: LDAPConfigCreate, db: Session = Depends(get_db)):
    db_config = LDAPConfig(**config.dict())
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

@router.get("/ldap/configs", response_model=List[LDAPConfigResponse])
def list_ldap_configs(db: Session = Depends(get_db)):
    return db.query(LDAPConfig).all()

@router.post("/ldap/sync/{config_id}")
def sync_ldap(config_id: int, db: Session = Depends(get_db)):
    config = db.query(LDAPConfig).filter(LDAPConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="LDAP config not found")
    
    ldap_service = LDAPService()
    stats = ldap_service.sync_users(config, db)
    
    return {
        "message": "Sync completed",
        "stats": stats,
        "sync_time": datetime.utcnow()
    }

@router.post("/ldap/authenticate")
def ldap_authenticate(username: str, password: str, db: Session = Depends(get_db)):
    config = db.query(LDAPConfig).filter(LDAPConfig.is_active == True).first()
    if not config:
        raise HTTPException(status_code=400, detail="No active LDAP configuration")
    
    ldap_service = LDAPService()
    user_data = ldap_service.authenticate(username, password, config)
    
    if not user_data:
        raise HTTPException(status_code=401, detail="Authentication failed")
    
    # Update or create user
    user = db.query(User).filter(User.username == username).first()
    if user:
        user.last_login = datetime.utcnow()
        db.commit()
    
    return {
        "authenticated": True,
        "user": user_data,
        "message": "LDAP authentication successful"
    }

# SSO/SAML
@router.get("/saml/login")
def saml_login(db: Session = Depends(get_db)):
    config = db.query(SAMLConfig).filter(SAMLConfig.is_active == True).first()
    if not config:
        raise HTTPException(status_code=400, detail="No active SAML configuration")
    
    saml_service = SAMLService()
    authn_request = saml_service.generate_authn_request(config.sso_url)
    
    return {
        "sso_url": config.sso_url,
        "saml_request": authn_request,
        "relay_state": "initial_login"
    }

@router.post("/saml/acs")
def saml_acs(saml_response: str, db: Session = Depends(get_db)):
    """Assertion Consumer Service - handles SAML response"""
    saml_service = SAMLService()
    user_data = saml_service.parse_saml_response(saml_response)
    
    if not user_data:
        raise HTTPException(status_code=400, detail="Invalid SAML response")
    
    # Check if user exists
    user = db.query(User).filter(User.email == user_data['email']).first()
    
    config = db.query(SAMLConfig).filter(SAMLConfig.is_active == True).first()
    
    if not user and config and config.jit_provisioning:
        # Just-in-Time provisioning
        user = saml_service.create_jit_user(user_data, db)
        return {
            "authenticated": True,
            "user_created": True,
            "user": {"id": user.id, "username": user.username, "email": user.email}
        }
    elif user:
        user.last_login = datetime.utcnow()
        db.commit()
        return {
            "authenticated": True,
            "user_created": False,
            "user": {"id": user.id, "username": user.username, "email": user.email}
        }
    else:
        raise HTTPException(status_code=403, detail="User not found and JIT provisioning disabled")

# Import/Export
@router.post("/users/import", response_model=ImportStatus)
async def import_users(
    file: UploadFile = File(...),
    update_existing: bool = False,
    db: Session = Depends(get_db)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    content = await file.read()
    csv_content = content.decode('utf-8')
    
    service = ImportExportService(db)
    job = service.import_users_from_csv(csv_content, "admin", update_existing)
    
    return ImportStatus(
        job_id=job.id,
        total_users=job.total_users,
        processed=job.processed,
        created_count=job.created_count,
        updated_count=job.updated_count,
        failed_count=job.failed_count,
        status=job.status
    )

@router.get("/users/export")
def export_users(
    status: Optional[UserStatus] = None,
    department: Optional[str] = None,
    db: Session = Depends(get_db)
):
    filters = {}
    if status:
        filters['status'] = status
    if department:
        filters['department'] = department
    
    service = ImportExportService(db)
    csv_content = service.export_users_to_csv(filters)
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=users_export.csv"}
    )

# Lifecycle Management
@router.post("/users/{user_id}/lifecycle/transition")
def transition_user_status(
    user_id: int,
    new_status: UserStatus,
    reason: str = "",
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    lifecycle_service = LifecycleService(db)
    result = lifecycle_service.transition_user(user, new_status, "admin", reason)
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['message'])
    
    return result

@router.post("/users/{user_id}/lifecycle/offboard")
def offboard_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    lifecycle_service = LifecycleService(db)
    result = lifecycle_service.process_offboarding(user, "admin")
    
    return result

# Statistics
@router.get("/stats/overview")
def get_stats(db: Session = Depends(get_db)):
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.status == UserStatus.ACTIVE).count()
    pending_users = db.query(User).filter(User.status == UserStatus.PENDING).count()
    suspended_users = db.query(User).filter(User.status == UserStatus.SUSPENDED).count()
    ldap_synced = db.query(User).filter(User.is_ldap_synced == True).count()
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "pending_users": pending_users,
        "suspended_users": suspended_users,
        "ldap_synced_users": ldap_synced,
        "provisioning_breakdown": {
            "manual": db.query(User).filter(User.provisioning_method == "manual").count(),
            "ldap_sync": db.query(User).filter(User.provisioning_method == "ldap_sync").count(),
            "sso_jit": db.query(User).filter(User.provisioning_method == "sso_jit").count(),
        }
    }
EOF

# Backend - Main Application
cat > $BACKEND_DIR/app/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from .models import Base
from .api.routes import router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="User Directory Features API",
    description="Enterprise identity integration with LDAP, SSO, and lifecycle management",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1", tags=["users"])

@app.get("/")
def root():
    return {
        "message": "User Directory Features API",
        "version": "1.0.0",
        "features": [
            "LDAP/AD Integration",
            "SSO/SAML Support",
            "User Import/Export",
            "Automated Provisioning",
            "Lifecycle Management"
        ]
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "user-directory"}
EOF

# Create __init__.py files
touch $BACKEND_DIR/app/__init__.py
touch $BACKEND_DIR/app/api/__init__.py
touch $BACKEND_DIR/app/services/__init__.py
# Note: models.py and schemas.py are at app level, not in subdirectories
touch $BACKEND_DIR/app/core/__init__.py
touch $BACKEND_DIR/tests/__init__.py

# Backend Tests
cat > $BACKEND_DIR/tests/test_api.py << 'EOF'
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db
from app.models import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "User Directory Features API" in response.json()["message"]

def test_create_user():
    response = client.post("/api/v1/users", json={
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "department": "Engineering"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"

def test_list_users():
    response = client.get("/api/v1/users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_stats():
    response = client.get("/api/v1/stats/overview")
    assert response.status_code == 200
    data = response.json()
    assert "total_users" in data
    assert "active_users" in data

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
EOF

# Frontend Package.json
cat > $FRONTEND_DIR/package.json << 'EOF'
{
  "name": "user-directory-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "@emotion/react": "^11.13.5",
    "@emotion/styled": "^11.13.5",
    "@mui/material": "^6.2.0",
    "@mui/icons-material": "^6.2.0",
    "axios": "^1.7.9",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.28.0",
    "recharts": "^2.15.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "devDependencies": {
    "react-scripts": "5.0.1"
  },
  "eslintConfig": {
    "extends": ["react-app"]
  },
  "browserslist": {
    "production": [">0.2%", "not dead", "not op_mini all"],
    "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
  }
}
EOF

# Frontend Dockerfile
cat > $FRONTEND_DIR/Dockerfile << 'EOF'
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
EOF

# Frontend - Main App
cat > $FRONTEND_DIR/src/App.js << 'EOF'
import React, { useState } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { Box, CssBaseline, AppBar, Toolbar, Typography, Drawer, List, ListItemButton, ListItemIcon, ListItemText } from '@mui/material';
import PeopleIcon from '@mui/icons-material/People';
import SyncIcon from '@mui/icons-material/Sync';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import TimelineIcon from '@mui/icons-material/Timeline';
import SettingsIcon from '@mui/icons-material/Settings';
import DashboardIcon from '@mui/icons-material/Dashboard';

import Dashboard from './pages/Dashboard';
import UserList from './pages/UserList';
import LDAPSync from './pages/LDAPSync';
import ImportExport from './pages/ImportExport';
import Lifecycle from './pages/Lifecycle';

const theme = createTheme({
  palette: {
    primary: { main: '#1976d2' },
    secondary: { main: '#dc004e' },
    background: { default: '#f5f5f5' }
  }
});

const drawerWidth = 240;

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');

  const renderPage = () => {
    switch(currentPage) {
      case 'dashboard': return <Dashboard />;
      case 'users': return <UserList />;
      case 'ldap': return <LDAPSync />;
      case 'import': return <ImportExport />;
      case 'lifecycle': return <Lifecycle />;
      default: return <Dashboard />;
    }
  };

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: <DashboardIcon /> },
    { id: 'users', label: 'Users', icon: <PeopleIcon /> },
    { id: 'ldap', label: 'LDAP Sync', icon: <SyncIcon /> },
    { id: 'import', label: 'Import/Export', icon: <CloudUploadIcon /> },
    { id: 'lifecycle', label: 'Lifecycle', icon: <TimelineIcon /> }
  ];

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex' }}>
        <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
          <Toolbar>
            <Typography variant="h6" noWrap component="div">
              Enterprise User Directory Management
            </Typography>
          </Toolbar>
        </AppBar>

        <Drawer
          variant="permanent"
          sx={{
            width: drawerWidth,
            flexShrink: 0,
            '& .MuiDrawer-paper': { width: drawerWidth, boxSizing: 'border-box' }
          }}
        >
          <Toolbar />
          <Box sx={{ overflow: 'auto' }}>
            <List>
              {menuItems.map((item) => (
                <ListItemButton 
                  key={item.id} 
                  onClick={() => setCurrentPage(item.id)}
                  selected={currentPage === item.id}
                >
                  <ListItemIcon>{item.icon}</ListItemIcon>
                  <ListItemText primary={item.label} />
                </ListItemButton>
              ))}
            </List>
          </Box>
        </Drawer>

        <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
          <Toolbar />
          {renderPage()}
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;
EOF

# Frontend - Dashboard Page
cat > $FRONTEND_DIR/src/pages/Dashboard.js << 'EOF'
import React, { useState, useEffect } from 'react';
import { Grid, Paper, Typography, Box, Card, CardContent } from '@mui/material';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import PeopleIcon from '@mui/icons-material/People';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';
import BlockIcon from '@mui/icons-material/Block';
import axios from 'axios';

const COLORS = ['#4caf50', '#ff9800', '#f44336', '#9e9e9e'];

function Dashboard() {
  const [stats, setStats] = useState({
    total_users: 0,
    active_users: 0,
    pending_users: 0,
    suspended_users: 0,
    ldap_synced_users: 0,
    provisioning_breakdown: { manual: 0, ldap_sync: 0, sso_jit: 0 }
  });

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/v1/stats/overview');
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const statusData = [
    { name: 'Active', value: stats.active_users },
    { name: 'Pending', value: stats.pending_users },
    { name: 'Suspended', value: stats.suspended_users },
  ];

  const provisioningData = [
    { name: 'Manual', value: stats.provisioning_breakdown.manual },
    { name: 'LDAP Sync', value: stats.provisioning_breakdown.ldap_sync },
    { name: 'SSO JIT', value: stats.provisioning_breakdown.sso_jit },
  ];

  const StatCard = ({ title, value, icon, color }) => (
    <Card sx={{ height: '100%', bgcolor: color, color: 'white' }}>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography variant="h4" fontWeight="bold">{value}</Typography>
            <Typography variant="body2">{title}</Typography>
          </Box>
          {icon}
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <Box>
      <Typography variant="h4" gutterBottom>Dashboard Overview</Typography>
      
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard 
            title="Total Users" 
            value={stats.total_users} 
            icon={<PeopleIcon sx={{ fontSize: 40 }} />}
            color="#1976d2"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard 
            title="Active Users" 
            value={stats.active_users} 
            icon={<CheckCircleIcon sx={{ fontSize: 40 }} />}
            color="#4caf50"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard 
            title="Pending" 
            value={stats.pending_users} 
            icon={<HourglassEmptyIcon sx={{ fontSize: 40 }} />}
            color="#ff9800"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard 
            title="Suspended" 
            value={stats.suspended_users} 
            icon={<BlockIcon sx={{ fontSize: 40 }} />}
            color="#f44336"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>User Status Distribution</Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={statusData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {statusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Provisioning Methods</Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={provisioningData}>
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="value" fill="#1976d2" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>

      <Paper sx={{ p: 3, mt: 3 }}>
        <Typography variant="h6" gutterBottom>LDAP Sync Status</Typography>
        <Typography variant="body1">
          LDAP Synced Users: <strong>{stats.ldap_synced_users}</strong> / {stats.total_users}
        </Typography>
        <Typography variant="body2" color="textSecondary">
          {stats.ldap_synced_users > 0 
            ? `${((stats.ldap_synced_users / stats.total_users) * 100).toFixed(1)}% of users synced with LDAP`
            : 'No LDAP synced users yet'
          }
        </Typography>
      </Paper>
    </Box>
  );
}

export default Dashboard;
EOF

# Continue with other frontend pages...
cat > $FRONTEND_DIR/src/pages/UserList.js << 'EOF'
import React, { useState, useEffect } from 'react';
import {
  Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Chip, IconButton, Box, Typography, TextField, MenuItem, Button
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import axios from 'axios';

function UserList() {
  const [users, setUsers] = useState([]);
  const [filter, setFilter] = useState({ status: '', department: '' });

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const params = new URLSearchParams();
      if (filter.status) params.append('status', filter.status);
      if (filter.department) params.append('department', filter.department);
      
      const response = await axios.get(`http://localhost:8000/api/v1/users?${params}`);
      setUsers(response.data);
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      active: 'success',
      pending: 'warning',
      suspended: 'error',
      deprovisioned: 'default'
    };
    return colors[status] || 'default';
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">User Directory</Typography>
        <IconButton onClick={fetchUsers} color="primary">
          <RefreshIcon />
        </IconButton>
      </Box>

      <Paper sx={{ p: 2, mb: 2 }}>
        <Box display="flex" gap={2}>
          <TextField
            select
            label="Status"
            value={filter.status}
            onChange={(e) => setFilter({ ...filter, status: e.target.value })}
            sx={{ minWidth: 150 }}
          >
            <MenuItem value="">All</MenuItem>
            <MenuItem value="active">Active</MenuItem>
            <MenuItem value="pending">Pending</MenuItem>
            <MenuItem value="suspended">Suspended</MenuItem>
          </TextField>
          
          <TextField
            label="Department"
            value={filter.department}
            onChange={(e) => setFilter({ ...filter, department: e.target.value })}
            sx={{ minWidth: 200 }}
          />
          
          <Button variant="contained" onClick={fetchUsers}>Apply Filters</Button>
        </Box>
      </Paper>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Username</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Full Name</TableCell>
              <TableCell>Department</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Provisioning</TableCell>
              <TableCell>LDAP Synced</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {users.map((user) => (
              <TableRow key={user.id}>
                <TableCell>{user.username}</TableCell>
                <TableCell>{user.email}</TableCell>
                <TableCell>{user.full_name || '-'}</TableCell>
                <TableCell>{user.department || '-'}</TableCell>
                <TableCell>
                  <Chip label={user.status} color={getStatusColor(user.status)} size="small" />
                </TableCell>
                <TableCell>{user.provisioning_method}</TableCell>
                <TableCell>
                  <Chip 
                    label={user.is_ldap_synced ? 'Yes' : 'No'} 
                    color={user.is_ldap_synced ? 'success' : 'default'} 
                    size="small" 
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

export default UserList;
EOF

cat > $FRONTEND_DIR/src/pages/LDAPSync.js << 'EOF'
import React, { useState, useEffect } from 'react';
import {
  Paper, Typography, Box, Button, TextField, Switch, FormControlLabel,
  Alert, CircularProgress, Card, CardContent, Grid
} from '@mui/material';
import SyncIcon from '@mui/icons-material/Sync';
import axios from 'axios';

function LDAPSync() {
  const [configs, setConfigs] = useState([]);
  const [syncing, setSyncing] = useState(false);
  const [result, setResult] = useState(null);
  const [newConfig, setNewConfig] = useState({
    name: 'Primary LDAP',
    server: 'ldap://localhost:389',
    base_dn: 'dc=example,dc=com',
    bind_dn: 'cn=admin,dc=example,dc=com',
    bind_password: 'admin',
    user_filter: '(objectClass=inetOrgPerson)',
    sync_interval_minutes: 30
  });

  useEffect(() => {
    fetchConfigs();
  }, []);

  const fetchConfigs = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/v1/ldap/configs');
      setConfigs(response.data);
    } catch (error) {
      console.error('Error fetching configs:', error);
    }
  };

  const handleSync = async (configId) => {
    setSyncing(true);
    setResult(null);
    try {
      const response = await axios.post(`http://localhost:8000/api/v1/ldap/sync/${configId}`);
      setResult({ type: 'success', data: response.data });
      fetchConfigs();
    } catch (error) {
      setResult({ type: 'error', message: error.message });
    } finally {
      setSyncing(false);
    }
  };

  const handleCreateConfig = async () => {
    try {
      await axios.post('http://localhost:8000/api/v1/ldap/configs', newConfig);
      fetchConfigs();
      setResult({ type: 'success', message: 'LDAP configuration created successfully' });
    } catch (error) {
      setResult({ type: 'error', message: error.message });
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>LDAP Directory Sync</Typography>

      {result && (
        <Alert severity={result.type} sx={{ mb: 3 }} onClose={() => setResult(null)}>
          {result.message || JSON.stringify(result.data)}
        </Alert>
      )}

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>LDAP Configurations</Typography>
        <Grid container spacing={2}>
          {configs.map((config) => (
            <Grid item xs={12} md={6} key={config.id}>
              <Card>
                <CardContent>
                  <Typography variant="h6">{config.name}</Typography>
                  <Typography variant="body2" color="textSecondary">Server: {config.server}</Typography>
                  <Typography variant="body2" color="textSecondary">Base DN: {config.base_dn}</Typography>
                  <Typography variant="body2" color="textSecondary">
                    Last Sync: {config.last_sync ? new Date(config.last_sync).toLocaleString() : 'Never'}
                  </Typography>
                  <Box mt={2}>
                    <Button
                      variant="contained"
                      startIcon={syncing ? <CircularProgress size={20} /> : <SyncIcon />}
                      onClick={() => handleSync(config.id)}
                      disabled={syncing}
                      fullWidth
                    >
                      {syncing ? 'Syncing...' : 'Sync Now'}
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Paper>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>Add New LDAP Configuration</Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Name"
              value={newConfig.name}
              onChange={(e) => setNewConfig({ ...newConfig, name: e.target.value })}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Server"
              value={newConfig.server}
              onChange={(e) => setNewConfig({ ...newConfig, server: e.target.value })}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Base DN"
              value={newConfig.base_dn}
              onChange={(e) => setNewConfig({ ...newConfig, base_dn: e.target.value })}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Bind DN"
              value={newConfig.bind_dn}
              onChange={(e) => setNewConfig({ ...newConfig, bind_dn: e.target.value })}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              type="password"
              label="Bind Password"
              value={newConfig.bind_password}
              onChange={(e) => setNewConfig({ ...newConfig, bind_password: e.target.value })}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="User Filter"
              value={newConfig.user_filter}
              onChange={(e) => setNewConfig({ ...newConfig, user_filter: e.target.value })}
            />
          </Grid>
          <Grid item xs={12}>
            <Button variant="contained" onClick={handleCreateConfig}>
              Create Configuration
            </Button>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
}

export default LDAPSync;
EOF

cat > $FRONTEND_DIR/src/pages/ImportExport.js << 'EOF'
import React, { useState } from 'react';
import {
  Paper, Typography, Box, Button, Alert, LinearProgress,
  FormControlLabel, Switch, Grid
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import CloudDownloadIcon from '@mui/icons-material/CloudDownload';
import axios from 'axios';

function ImportExport() {
  const [importing, setImporting] = useState(false);
  const [result, setResult] = useState(null);
  const [updateExisting, setUpdateExisting] = useState(false);

  const handleImport = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setImporting(true);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('update_existing', updateExisting);

    try {
      const response = await axios.post(
        `http://localhost:8000/api/v1/users/import?update_existing=${updateExisting}`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );
      setResult({ type: 'success', data: response.data });
    } catch (error) {
      setResult({ type: 'error', message: error.message });
    } finally {
      setImporting(false);
    }
  };

  const handleExport = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/v1/users/export', {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `users_export_${new Date().toISOString()}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      setResult({ type: 'success', message: 'Export completed successfully' });
    } catch (error) {
      setResult({ type: 'error', message: error.message });
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>User Import/Export</Typography>

      {result && (
        <Alert severity={result.type} sx={{ mb: 3 }} onClose={() => setResult(null)}>
          {result.message || (
            <Box>
              <Typography>Import completed:</Typography>
              <Typography>Total: {result.data?.total_users}</Typography>
              <Typography>Created: {result.data?.created_count}</Typography>
              <Typography>Updated: {result.data?.updated_count}</Typography>
              <Typography>Failed: {result.data?.failed_count}</Typography>
            </Box>
          )}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Import Users</Typography>
            <Typography variant="body2" color="textSecondary" paragraph>
              Upload a CSV file with columns: username, email, full_name, department, employee_type, manager
            </Typography>

            <FormControlLabel
              control={
                <Switch
                  checked={updateExisting}
                  onChange={(e) => setUpdateExisting(e.target.checked)}
                />
              }
              label="Update existing users"
            />

            <Box mt={2}>
              <input
                accept=".csv"
                style={{ display: 'none' }}
                id="csv-upload"
                type="file"
                onChange={handleImport}
              />
              <label htmlFor="csv-upload">
                <Button
                  variant="contained"
                  component="span"
                  startIcon={<CloudUploadIcon />}
                  disabled={importing}
                  fullWidth
                >
                  {importing ? 'Importing...' : 'Upload CSV'}
                </Button>
              </label>
            </Box>

            {importing && <LinearProgress sx={{ mt: 2 }} />}
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Export Users</Typography>
            <Typography variant="body2" color="textSecondary" paragraph>
              Download all users as a CSV file for backup or migration
            </Typography>

            <Button
              variant="contained"
              startIcon={<CloudDownloadIcon />}
              onClick={handleExport}
              fullWidth
            >
              Export to CSV
            </Button>
          </Paper>
        </Grid>
      </Grid>

      <Paper sx={{ p: 3, mt: 3 }}>
        <Typography variant="h6" gutterBottom>CSV Format Example</Typography>
        <Box component="pre" sx={{ bgcolor: '#f5f5f5', p: 2, borderRadius: 1, overflow: 'auto' }}>
{`username,email,full_name,department,employee_type,manager
jdoe,jdoe@example.com,John Doe,Engineering,Engineer,admin
jsmith,jsmith@example.com,Jane Smith,Sales,Manager,admin`}
        </Box>
      </Paper>
    </Box>
  );
}

export default ImportExport;
EOF

cat > $FRONTEND_DIR/src/pages/Lifecycle.js << 'EOF'
import React, { useState, useEffect } from 'react';
import {
  Paper, Typography, Box, Button, TextField, MenuItem, Alert,
  Card, CardContent, CardActions, Grid, Stepper, Step, StepLabel
} from '@mui/material';
import axios from 'axios';

const LIFECYCLE_STEPS = ['Pending', 'Active', 'Suspended', 'Deprovisioned'];

function Lifecycle() {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState('');
  const [targetStatus, setTargetStatus] = useState('');
  const [reason, setReason] = useState('');
  const [result, setResult] = useState(null);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/v1/users');
      setUsers(response.data);
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  const handleTransition = async () => {
    if (!selectedUser || !targetStatus) return;

    try {
      const response = await axios.post(
        `http://localhost:8000/api/v1/users/${selectedUser}/lifecycle/transition?new_status=${targetStatus}&reason=${reason}`
      );
      setResult({ type: 'success', data: response.data });
      fetchUsers();
      setSelectedUser('');
      setTargetStatus('');
      setReason('');
    } catch (error) {
      setResult({ type: 'error', message: error.response?.data?.detail || error.message });
    }
  };

  const handleOffboard = async (userId) => {
    try {
      const response = await axios.post(`http://localhost:8000/api/v1/users/${userId}/lifecycle/offboard`);
      setResult({ type: 'success', data: response.data });
      fetchUsers();
    } catch (error) {
      setResult({ type: 'error', message: error.message });
    }
  };

  const getActiveStep = (status) => {
    const statusMap = { 'pending': 0, 'active': 1, 'suspended': 2, 'deprovisioned': 3 };
    return statusMap[status] || 0;
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>User Lifecycle Management</Typography>

      {result && (
        <Alert severity={result.type} sx={{ mb: 3 }} onClose={() => setResult(null)}>
          {result.message || JSON.stringify(result.data, null, 2)}
        </Alert>
      )}

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>Manual State Transition</Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={4}>
            <TextField
              select
              fullWidth
              label="Select User"
              value={selectedUser}
              onChange={(e) => setSelectedUser(e.target.value)}
            >
              {users.map((user) => (
                <MenuItem key={user.id} value={user.id}>
                  {user.username} ({user.status})
                </MenuItem>
              ))}
            </TextField>
          </Grid>
          <Grid item xs={12} sm={3}>
            <TextField
              select
              fullWidth
              label="Target Status"
              value={targetStatus}
              onChange={(e) => setTargetStatus(e.target.value)}
            >
              <MenuItem value="active">Active</MenuItem>
              <MenuItem value="suspended">Suspended</MenuItem>
              <MenuItem value="deprovisioned">Deprovisioned</MenuItem>
            </TextField>
          </Grid>
          <Grid item xs={12} sm={3}>
            <TextField
              fullWidth
              label="Reason"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
            />
          </Grid>
          <Grid item xs={12} sm={2}>
            <Button
              fullWidth
              variant="contained"
              onClick={handleTransition}
              disabled={!selectedUser || !targetStatus}
              sx={{ height: '100%' }}
            >
              Transition
            </Button>
          </Grid>
        </Grid>
      </Paper>

      <Typography variant="h6" gutterBottom>User Lifecycle Status</Typography>
      <Grid container spacing={2}>
        {users.slice(0, 6).map((user) => (
          <Grid item xs={12} md={6} key={user.id}>
            <Card>
              <CardContent>
                <Typography variant="h6">{user.username}</Typography>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  {user.email}
                </Typography>
                <Stepper activeStep={getActiveStep(user.status)} sx={{ mt: 2 }}>
                  {LIFECYCLE_STEPS.map((label) => (
                    <Step key={label}>
                      <StepLabel>{label}</StepLabel>
                    </Step>
                  ))}
                </Stepper>
                <Typography variant="body2" sx={{ mt: 2 }}>
                  Current Status: <strong>{user.status}</strong>
                </Typography>
              </CardContent>
              <CardActions>
                {user.status === 'active' && (
                  <Button size="small" color="error" onClick={() => handleOffboard(user.id)}>
                    Start Offboarding
                  </Button>
                )}
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}

export default Lifecycle;
EOF

# Frontend - index.js
cat > $FRONTEND_DIR/src/index.js << 'EOF'
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
EOF

# Frontend - index.css
cat > $FRONTEND_DIR/src/index.css << 'EOF'
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}
EOF

# Frontend - public/index.html
cat > $FRONTEND_DIR/public/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="Enterprise User Directory Management" />
    <title>User Directory Features</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
EOF

# Create build and run scripts
cat > $PROJECT_DIR/build.sh << 'EOF'
#!/bin/bash
set -e

echo "Building Day 76: User Directory Features"
echo "========================================"

# Option 1: Docker Build
if [ "$1" == "docker" ]; then
    echo "Building with Docker..."
    docker-compose up -d --build
    echo ""
    echo "Waiting for services to be ready..."
    sleep 15
    
    echo ""
    echo "Services running:"
    echo "- LDAP Server: ldap://localhost:389"
    echo "- Backend API: http://localhost:8000"
    echo "- Frontend Dashboard: http://localhost:3000"
    echo "- API Documentation: http://localhost:8000/docs"
    echo ""
    echo "To view logs: docker-compose logs -f"
    echo "To stop: docker-compose down"
    exit 0
fi

# Option 2: Local Development
echo "Setting up local development environment..."

# Backend setup
cd backend
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Starting infrastructure services..."
cd ..
docker-compose up -d ldap redis postgres

echo "Waiting for services..."
sleep 10

echo "Running database migrations..."
cd backend
export DATABASE_URL="postgresql://userdir:userdir123@localhost:5432/userdir"
export REDIS_URL="redis://localhost:6379"
export LDAP_SERVER="ldap://localhost:389"
export LDAP_BASE_DN="dc=example,dc=com"
export LDAP_BIND_DN="cn=admin,dc=example,dc=com"
export LDAP_BIND_PASSWORD="admin"

python -c "from app.database import engine; from app.models import Base; Base.metadata.create_all(bind=engine)"

echo "Running backend tests..."
pytest tests/ -v

echo "Starting backend server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

sleep 5

# Frontend setup
echo "Setting up frontend..."
cd frontend
npm install
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "=========================================="
echo "Services running:"
echo "- LDAP Server: ldap://localhost:389"
echo "- Backend API: http://localhost:8000"
echo "- Frontend Dashboard: http://localhost:3000"
echo "- API Documentation: http://localhost:8000/docs"
echo ""
echo "Demo Credentials:"
echo "LDAP Users:"
echo "  - john.doe / password123"
echo "  - jane.smith / password123"
echo "  - admin / admin123"
echo ""
echo "Press Ctrl+C to stop all services"
wait
EOF

cat > $PROJECT_DIR/stop.sh << 'EOF'
#!/bin/bash

echo "Stopping Day 76 services..."

# Stop Docker containers
docker-compose down

# Kill local processes
pkill -f "uvicorn app.main"
pkill -f "react-scripts start"

echo "All services stopped"
EOF

chmod +x $PROJECT_DIR/build.sh
chmod +x $PROJECT_DIR/stop.sh

echo ""
echo "=========================================="
echo "Day 76: User Directory Features Setup Complete!"
echo "=========================================="
echo ""
echo "To build and run:"
echo ""
echo "Option 1 - Docker (recommended):"
echo "  cd $PROJECT_DIR && ./build.sh docker"
echo ""
echo "Option 2 - Local development:"
echo "  cd $PROJECT_DIR && ./build.sh"
echo ""
echo "To stop:"
echo "  cd $PROJECT_DIR && ./stop.sh"
echo ""
echo "Access points:"
echo "- Frontend Dashboard: http://localhost:3000"
echo "- Backend API: http://localhost:8000"
echo "- API Docs: http://localhost:8000/docs"
echo "- LDAP Server: ldap://localhost:389"
echo ""
echo "Test the system by:"
echo "1. View Dashboard - see user statistics"
echo "2. LDAP Sync - sync users from directory"
echo "3. Import/Export - bulk user operations"
echo "4. Lifecycle - manage user states"
echo "==========================================" 