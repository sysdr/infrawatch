from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime

from ..models.server_models import Template, Server, Group
from ..schemas.server_schemas import TemplateCreate, TemplateResponse, TemplateDeployRequest

async def create_template(db: Session, template: TemplateCreate) -> TemplateResponse:
    """Create a new server template"""
    db_template = Template(**template.dict())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return TemplateResponse.model_validate(db_template)

async def list_templates(db: Session) -> List[TemplateResponse]:
    """List all templates"""
    templates = db.query(Template).all()
    return [TemplateResponse.model_validate(template) for template in templates]

async def deploy_from_template(db: Session, template_id: int, deploy_request: TemplateDeployRequest) -> Dict[str, Any]:
    """Deploy servers from template"""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise ValueError("Template not found")
    
    # Merge template config with overrides
    config = template.config.copy()
    config.update(deploy_request.override_config)
    
    created_servers = []
    
    for i in range(deploy_request.count):
        server_name = f"{deploy_request.name_prefix}-{i+1:03d}"
        
        server_data = {
            "name": server_name,
            "hostname": f"{server_name}.local",
            "region": config.get("region", "us-east-1"),
            "instance_type": config.get("instance_type", "t3.micro"),
            "cpu_cores": config.get("cpu_cores", 2),
            "memory_gb": config.get("memory_gb", 4),
            "storage_gb": config.get("storage_gb", 20),
            "os_type": config.get("os_type", "ubuntu-20.04"),
            "tags": config.get("tags", {}),
            "status": "starting"
        }
        
        server = Server(**server_data)
        db.add(server)
        db.flush()  # Get the ID
        
        # Add to group if specified
        if deploy_request.group_id:
            group = db.query(Group).filter(Group.id == deploy_request.group_id).first()
            if group:
                server.groups.append(group)
        
        created_servers.append({
            "id": server.id,
            "name": server.name,
            "hostname": server.hostname
        })
    
    db.commit()
    
    return {
        "template_id": template_id,
        "created_servers": created_servers,
        "count": len(created_servers)
    }
