from sqlalchemy.orm import Session
from app.models.template import Template, ReportFormat
from jinja2 import Environment, BaseLoader, TemplateSyntaxError
from typing import Dict, Any, List
import re

class TemplateService:
    
    @staticmethod
    def create_template(db: Session, name: str, content: str, 
                       format: ReportFormat = ReportFormat.HTML,
                       description: str = None, variables: List[str] = None) -> Template:
        """Create a new template"""
        # Extract variables from template if not provided
        if variables is None:
            variables = TemplateService.extract_variables(content)
        
        template = Template(
            name=name,
            description=description,
            content=content,
            format=format,
            variables=variables,
            version=1
        )
        db.add(template)
        db.commit()
        db.refresh(template)
        return template
    
    @staticmethod
    def extract_variables(content: str) -> List[str]:
        """Extract Jinja2 variables from template content"""
        pattern = r'\{\{\s*([a-zA-Z_][a-zA-Z0-9_\.]*)\s*\}\}'
        matches = re.findall(pattern, content)
        return list(set(matches))
    
    @staticmethod
    def validate_template(content: str) -> tuple[bool, str]:
        """Validate Jinja2 template syntax"""
        try:
            env = Environment(loader=BaseLoader())
            env.parse(content)
            return True, "Template is valid"
        except TemplateSyntaxError as e:
            return False, str(e)
    
    @staticmethod
    def render_template(template: Template, data: Dict[str, Any]) -> str:
        """Render template with data"""
        env = Environment(loader=BaseLoader())
        jinja_template = env.from_string(template.content)
        return jinja_template.render(**data)
    
    @staticmethod
    def get_all_templates(db: Session, active_only: bool = False) -> List[Template]:
        """Get all templates"""
        query = db.query(Template)
        if active_only:
            query = query.filter(Template.is_active == True)
        return query.order_by(Template.created_at.desc()).all()
    
    @staticmethod
    def get_template(db: Session, template_id: int) -> Template:
        """Get template by ID"""
        return db.query(Template).filter(Template.id == template_id).first()
    
    @staticmethod
    def update_template(db: Session, template_id: int, **kwargs) -> Template:
        """Update template (creates new version)"""
        template = db.query(Template).filter(Template.id == template_id).first()
        if not template:
            return None
        
        # Create new version
        new_version = template.version + 1
        for key, value in kwargs.items():
            if hasattr(template, key):
                setattr(template, key, value)
        template.version = new_version
        
        db.commit()
        db.refresh(template)
        return template
    
    @staticmethod
    def delete_template(db: Session, template_id: int) -> bool:
        """Soft delete template"""
        template = db.query(Template).filter(Template.id == template_id).first()
        if template:
            template.is_active = False
            db.commit()
            return True
        return False
