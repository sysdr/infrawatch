from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from sqlalchemy import create_engine, Column, String, DateTime, Boolean, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta
import os
import json
import paramiko
import threading
import schedule
import time
from typing import List, Optional
from pydantic import BaseModel
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ed25519
from cryptography.hazmat.backends import default_backend
import base64
import uuid
from passlib.context import CryptContext

app = FastAPI(title="Server Authentication System", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./auth.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Models
class SSHKey(Base):
    __tablename__ = "ssh_keys"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, index=True)
    public_key = Column(Text)
    private_key = Column(Text)  # Encrypted
    key_type = Column(String, default="rsa")
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    status = Column(String, default="active")
    last_used = Column(DateTime)

class Server(Base):
    __tablename__ = "servers"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True)
    hostname = Column(String)
    port = Column(Integer, default=22)
    username = Column(String)
    ssh_key_id = Column(String)
    status = Column(String, default="unknown")
    last_check = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuthLog(Base):
    __tablename__ = "auth_logs"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    server_id = Column(String)
    ssh_key_id = Column(String)
    action = Column(String)
    status = Column(String)
    details = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models
class SSHKeyCreate(BaseModel):
    name: str
    key_type: str = "rsa"
    expires_days: int = 90

class SSHKeyResponse(BaseModel):
    id: str
    name: str
    key_type: str
    status: str
    created_at: datetime
    expires_at: Optional[datetime]
    last_used: Optional[datetime]

class ServerCreate(BaseModel):
    name: str
    hostname: str
    port: int = 22
    username: str
    ssh_key_id: str

class ServerResponse(BaseModel):
    id: str
    name: str
    hostname: str
    port: int
    username: str
    ssh_key_id: str
    status: str
    last_check: Optional[datetime]

class ConnectionTest(BaseModel):
    server_id: str

class KeyRotationRequest(BaseModel):
    ssh_key_id: str

# Utility functions
def generate_ssh_key(key_type: str = "rsa"):
    """Generate SSH key pair"""
    if key_type == "rsa":
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
    else:  # ed25519
        private_key = ed25519.Ed25519PrivateKey.generate()
    
    # Get private key in PEM format
    pem_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # Get public key in OpenSSH format
    public_key = private_key.public_key()
    ssh_public = public_key.public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH
    )
    
    return pem_private.decode('utf-8'), ssh_public.decode('utf-8')

def test_ssh_connection(hostname: str, port: int, username: str, private_key_str: str):
    """Test SSH connection to server"""
    try:
        # Create SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Load private key
        private_key = paramiko.RSAKey.from_private_key_string(private_key_str)
        
        # Connect
        ssh.connect(
            hostname=hostname,
            port=port,
            username=username,
            pkey=private_key,
            timeout=10
        )
        
        # Test command execution
        stdin, stdout, stderr = ssh.exec_command('echo "Connection test successful"')
        result = stdout.read().decode()
        
        ssh.close()
        return {"success": True, "message": result.strip()}
        
    except Exception as e:
        return {"success": False, "message": str(e)}

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Server Authentication System", "status": "running"}

@app.post("/ssh-keys/", response_model=SSHKeyResponse)
async def create_ssh_key(key_data: SSHKeyCreate, db: Session = Depends(get_db)):
    """Generate new SSH key pair"""
    try:
        # Generate key pair
        private_key, public_key = generate_ssh_key(key_data.key_type)
        
        # Calculate expiration
        expires_at = datetime.utcnow() + timedelta(days=key_data.expires_days)
        
        # Create database record
        ssh_key = SSHKey(
            name=key_data.name,
            public_key=public_key,
            private_key=private_key,  # In production, encrypt this
            key_type=key_data.key_type,
            expires_at=expires_at
        )
        
        db.add(ssh_key)
        db.commit()
        db.refresh(ssh_key)
        
        return ssh_key
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/ssh-keys/", response_model=List[SSHKeyResponse])
async def list_ssh_keys(db: Session = Depends(get_db)):
    """List all SSH keys"""
    keys = db.query(SSHKey).all()
    return keys

@app.get("/ssh-keys/{key_id}")
async def get_ssh_key_details(key_id: str, db: Session = Depends(get_db)):
    """Get SSH key details including public key"""
    key = db.query(SSHKey).filter(SSHKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="SSH key not found")
    
    return {
        "id": key.id,
        "name": key.name,
        "public_key": key.public_key,
        "key_type": key.key_type,
        "status": key.status,
        "created_at": key.created_at,
        "expires_at": key.expires_at
    }

@app.post("/ssh-keys/{key_id}/rotate")
async def rotate_ssh_key(key_id: str, db: Session = Depends(get_db)):
    """Rotate SSH key"""
    key = db.query(SSHKey).filter(SSHKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="SSH key not found")
    
    try:
        # Generate new key pair
        private_key, public_key = generate_ssh_key(key.key_type)
        
        # Update key
        key.private_key = private_key
        key.public_key = public_key
        key.status = "active"
        key.created_at = datetime.utcnow()
        key.expires_at = datetime.utcnow() + timedelta(days=90)
        
        db.commit()
        
        # Log rotation
        log_entry = AuthLog(
            ssh_key_id=key_id,
            action="key_rotation",
            status="success",
            details="SSH key rotated successfully"
        )
        db.add(log_entry)
        db.commit()
        
        return {"message": "SSH key rotated successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/servers/", response_model=ServerResponse)
async def create_server(server_data: ServerCreate, db: Session = Depends(get_db)):
    """Add new server"""
    server = Server(**server_data.dict())
    db.add(server)
    db.commit()
    db.refresh(server)
    return server

@app.get("/servers/", response_model=List[ServerResponse])
async def list_servers(db: Session = Depends(get_db)):
    """List all servers"""
    servers = db.query(Server).all()
    return servers

@app.post("/test-connection/")
async def test_connection(test_data: ConnectionTest, db: Session = Depends(get_db)):
    """Test SSH connection to server"""
    server = db.query(Server).filter(Server.id == test_data.server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    ssh_key = db.query(SSHKey).filter(SSHKey.id == server.ssh_key_id).first()
    if not ssh_key:
        raise HTTPException(status_code=404, detail="SSH key not found")
    
    # Test connection
    result = test_ssh_connection(
        server.hostname,
        server.port,
        server.username,
        ssh_key.private_key
    )
    
    # Update server status
    server.status = "connected" if result["success"] else "failed"
    server.last_check = datetime.utcnow()
    
    # Update key last used
    if result["success"]:
        ssh_key.last_used = datetime.utcnow()
    
    db.commit()
    
    # Log connection attempt
    log_entry = AuthLog(
        server_id=server.id,
        ssh_key_id=ssh_key.id,
        action="connection_test",
        status="success" if result["success"] else "failure",
        details=result["message"]
    )
    db.add(log_entry)
    db.commit()
    
    return result

@app.get("/auth-logs/")
async def get_auth_logs(limit: int = 50, db: Session = Depends(get_db)):
    """Get authentication logs"""
    logs = db.query(AuthLog).order_by(AuthLog.timestamp.desc()).limit(limit).all()
    return logs

@app.get("/dashboard/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    total_keys = db.query(SSHKey).count()
    active_keys = db.query(SSHKey).filter(SSHKey.status == "active").count()
    total_servers = db.query(Server).count()
    connected_servers = db.query(Server).filter(Server.status == "connected").count()
    
    # Recent activity
    recent_logs = db.query(AuthLog).order_by(AuthLog.timestamp.desc()).limit(10).all()
    
    return {
        "total_keys": total_keys,
        "active_keys": active_keys,
        "total_servers": total_servers,
        "connected_servers": connected_servers,
        "recent_activity": [
            {
                "action": log.action,
                "status": log.status,
                "timestamp": log.timestamp,
                "details": log.details
            } for log in recent_logs
        ]
    }

# Background tasks for key rotation monitoring
def check_expiring_keys():
    """Background task to check for expiring keys"""
    db = SessionLocal()
    try:
        expiring_soon = db.query(SSHKey).filter(
            SSHKey.expires_at < datetime.utcnow() + timedelta(days=7),
            SSHKey.status == "active"
        ).all()
        
        for key in expiring_soon:
            key.status = "expiring_soon"
            log_entry = AuthLog(
                ssh_key_id=key.id,
                action="expiration_warning",
                status="warning",
                details=f"SSH key '{key.name}' expires in less than 7 days"
            )
            db.add(log_entry)
        
        db.commit()
    finally:
        db.close()

# Schedule background tasks
schedule.every(1).hours.do(check_expiring_keys)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)

# Start background scheduler
scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
