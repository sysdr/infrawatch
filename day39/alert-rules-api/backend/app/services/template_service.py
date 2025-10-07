from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.models.database import RuleTemplate, AlertRule
from app.models.templates import RuleTemplateCreate, TemplatePreset
from app.models.rules import AlertRuleCreate

class TemplateService:
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_template(self, template_data: RuleTemplateCreate) -> RuleTemplate:
        """Create a new rule template"""
        
        # Check for duplicate names
        existing = self.db.query(RuleTemplate).filter(
            RuleTemplate.name == template_data.name
        ).first()
        if existing:
            raise ValueError(f"Template with name '{template_data.name}' already exists")
        
        db_template = RuleTemplate(
            name=template_data.name,
            description=template_data.description,
            category=template_data.category,
            template_config=template_data.template_config,
            is_public=template_data.is_public
        )
        
        self.db.add(db_template)
        self.db.commit()
        self.db.refresh(db_template)
        
        return db_template
    
    def get_templates(self, category: Optional[str] = None, 
                     public_only: bool = True) -> List[RuleTemplate]:
        """Get templates with optional filtering"""
        query = self.db.query(RuleTemplate)
        
        if public_only:
            query = query.filter(RuleTemplate.is_public == True)
        
        if category:
            query = query.filter(RuleTemplate.category == category)
        
        return query.all()
    
    def get_template(self, template_id: int) -> Optional[RuleTemplate]:
        """Get single template by ID"""
        return self.db.query(RuleTemplate).filter(RuleTemplate.id == template_id).first()
    
    def create_rule_from_template(self, template_id: int, 
                                rule_name: str, 
                                overrides: Dict[str, Any] = None) -> AlertRuleCreate:
        """Create rule configuration from template"""
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template with ID {template_id} not found")
        
        config = template.template_config.copy()
        
        # Apply overrides
        if overrides:
            config.update(overrides)
        
        # Create rule data
        rule_data = AlertRuleCreate(
            name=rule_name,
            description=f"Created from template: {template.name}",
            expression=config.get('expression', ''),
            severity=config.get('severity', 'warning'),
            enabled=config.get('enabled', True),
            tags=config.get('tags', []),
            thresholds=config.get('thresholds', {}),
            template_id=template_id
        )
        
        return rule_data
    
    def initialize_default_templates(self):
        """Initialize system with default templates"""
        default_templates = [
            TemplatePreset.CPU_UTILIZATION,
            TemplatePreset.MEMORY_UTILIZATION,
            TemplatePreset.API_RESPONSE_TIME
        ]
        
        for template_data in default_templates:
            existing = self.db.query(RuleTemplate).filter(
                RuleTemplate.name == template_data['name']
            ).first()
            
            if not existing:
                template = RuleTemplate(**template_data)
                self.db.add(template)
        
        self.db.commit()
        print("✅ Default templates initialized")
