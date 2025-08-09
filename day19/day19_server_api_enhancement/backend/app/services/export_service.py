from sqlalchemy.orm import Session
from fastapi import UploadFile
import pandas as pd
import json
import io
from typing import Tuple, Optional
from datetime import datetime

from ..models.server_models import Server, Group

async def import_servers(db: Session, file: UploadFile) -> dict:
    """Import servers from CSV or Excel file"""
    content = await file.read()
    
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise ValueError("Unsupported file format. Use CSV or Excel.")
        
        # Validate required columns
        required_columns = ['name', 'hostname']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        created_servers = []
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Parse tags if it's a string
                tags = {}
                if 'tags' in row and pd.notna(row['tags']):
                    if isinstance(row['tags'], str):
                        tags = json.loads(row['tags'])
                    elif isinstance(row['tags'], dict):
                        tags = row['tags']
                
                server_data = {
                    "name": row['name'],
                    "hostname": row['hostname'],
                    "ip_address": row.get('ip_address'),
                    "region": row.get('region'),
                    "instance_type": row.get('instance_type'),
                    "cpu_cores": int(row['cpu_cores']) if pd.notna(row.get('cpu_cores')) else None,
                    "memory_gb": int(row['memory_gb']) if pd.notna(row.get('memory_gb')) else None,
                    "storage_gb": int(row['storage_gb']) if pd.notna(row.get('storage_gb')) else None,
                    "os_type": row.get('os_type'),
                    "tags": tags,
                    "status": row.get('status', 'unknown')
                }
                
                # Remove None values
                server_data = {k: v for k, v in server_data.items() if v is not None}
                
                server = Server(**server_data)
                db.add(server)
                db.flush()
                
                created_servers.append({
                    "id": server.id,
                    "name": server.name,
                    "hostname": server.hostname
                })
                
            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")
        
        db.commit()
        
        return {
            "created_count": len(created_servers),
            "error_count": len(errors),
            "created_servers": created_servers,
            "errors": errors
        }
        
    except Exception as e:
        raise ValueError(f"Failed to process file: {str(e)}")

async def export_servers(db: Session, format: str, group_id: Optional[int] = None) -> Tuple[bytes, str, str]:
    """Export servers to CSV or Excel format"""
    
    query = db.query(Server)
    
    if group_id:
        query = query.join(Server.groups).filter(Group.id == group_id)
    
    servers = query.all()
    
    # Convert to DataFrame
    data = []
    for server in servers:
        data.append({
            "id": server.id,
            "name": server.name,
            "hostname": server.hostname,
            "ip_address": server.ip_address,
            "status": server.status,
            "region": server.region,
            "instance_type": server.instance_type,
            "cpu_cores": server.cpu_cores,
            "memory_gb": server.memory_gb,
            "storage_gb": server.storage_gb,
            "os_type": server.os_type,
            "tags": json.dumps(server.tags) if server.tags else "",
            "created_at": server.created_at.isoformat() if server.created_at else "",
            "updated_at": server.updated_at.isoformat() if server.updated_at else ""
        })
    
    df = pd.DataFrame(data)
    
    if format == "csv":
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        content = buffer.getvalue().encode('utf-8')
        filename = f"servers_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        media_type = "text/csv"
    else:  # excel
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False, engine='openpyxl')
        content = buffer.getvalue()
        filename = f"servers_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    return content, filename, media_type
