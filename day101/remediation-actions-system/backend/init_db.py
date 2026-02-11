from app.models.remediation import Base, ActionTemplate, RiskLevel
from app.core.database import engine, SessionLocal

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    templates = [
        {"name": "Block Suspicious IP", "description": "Block IP address showing suspicious activity",
         "risk_level": RiskLevel.LOW, "script_name": "block_ip.sh",
         "parameters_schema": {"type": "object", "properties": {"ip_address": {"type": "string"}, "duration_hours": {"type": "integer", "default": 24}}, "required": ["ip_address"]},
         "requires_approval": False, "max_blast_radius": 1, "can_rollback": True, "rollback_script": "unblock_ip.sh"},
        {"name": "Rotate Database Credentials", "description": "Rotate database credentials for compromised service",
         "risk_level": RiskLevel.HIGH, "script_name": "rotate_db_creds.sh",
         "parameters_schema": {"type": "object", "properties": {"database_name": {"type": "string"}, "service_name": {"type": "string"}}, "required": ["database_name", "service_name"]},
         "requires_approval": True, "max_blast_radius": 10, "can_rollback": True, "rollback_script": "restore_db_creds.sh"},
        {"name": "Isolate Compromised Instance", "description": "Isolate EC2 instance from network",
         "risk_level": RiskLevel.MEDIUM, "script_name": "isolate_instance.sh",
         "parameters_schema": {"type": "object", "properties": {"instance_id": {"type": "string"}, "preserve_data": {"type": "boolean", "default": True}}, "required": ["instance_id"]},
         "requires_approval": True, "max_blast_radius": 1, "can_rollback": True, "rollback_script": "restore_instance_network.sh"},
        {"name": "Emergency Service Restart", "description": "Restart unresponsive service",
         "risk_level": RiskLevel.MEDIUM, "script_name": "restart_service.sh",
         "parameters_schema": {"type": "object", "properties": {"service_name": {"type": "string"}, "graceful_shutdown": {"type": "boolean", "default": True}}, "required": ["service_name"]},
         "requires_approval": False, "max_blast_radius": 5, "can_rollback": False, "rollback_script": None},
    ]
    
    for t in templates:
        if not db.query(ActionTemplate).filter(ActionTemplate.name == t["name"]).first():
            db.add(ActionTemplate(**t))
    db.commit()
    print("✓ Database initialized with sample templates")

if __name__ == "__main__":
    init_db()
