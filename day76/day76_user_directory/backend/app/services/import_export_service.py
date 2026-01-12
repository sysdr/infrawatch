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
