from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, desc
from . import models, schemas
import semver
import json
import re
from typing import List, Optional, Dict, Any
from datetime import datetime

class TemplateService:
    
    @staticmethod
    def get_next_version(current_version: str, change_type: str = "patch") -> str:
        """Calculate next semantic version based on change type"""
        try:
            ver = semver.VersionInfo.parse(current_version)
            if change_type == "major":
                return str(ver.bump_major())
            elif change_type == "minor":
                return str(ver.bump_minor())
            else:
                return str(ver.bump_patch())
        except:
            return "1.0.0"
    
    @staticmethod
    def detect_change_type(old_config: Dict, new_config: Dict) -> str:
        """Detect if changes are breaking (major), feature (minor), or fix (patch)"""
        old_widgets = old_config.get("widgets", [])
        new_widgets = new_config.get("widgets", [])
        
        # Widget removed = breaking change
        old_widget_ids = {w.get("id") for w in old_widgets}
        new_widget_ids = {w.get("id") for w in new_widgets}
        if old_widget_ids - new_widget_ids:
            return "major"
        
        # New widget = feature
        if new_widget_ids - old_widget_ids:
            return "minor"
        
        # Otherwise patch
        return "patch"
    
    @staticmethod
    def substitute_variables(config: Dict, variable_values: Dict[str, Any]) -> Dict:
        """Replace {{variable}} patterns in config with actual values"""
        config_str = json.dumps(config)
        
        for var_name, var_value in variable_values.items():
            pattern = f"{{{{{var_name}}}}}"
            config_str = config_str.replace(pattern, str(var_value))
        
        return json.loads(config_str)
    
    @staticmethod
    def extract_variables(config: Dict) -> List[str]:
        """Extract all {{variable}} patterns from config"""
        config_str = json.dumps(config)
        pattern = r'\{\{(\w+)\}\}'
        return list(set(re.findall(pattern, config_str)))
    
    @staticmethod
    def create_template(db: Session, template: schemas.TemplateCreate, author_id: int) -> models.Template:
        """Create a new template with version 1.0.0"""
        db_template = models.Template(
            name=template.name,
            description=template.description,
            version="1.0.0",
            config=template.config,
            author_id=author_id,
            visibility=template.visibility,
            role_access=template.role_access,
            category=template.category,
            tags=template.tags,
            status="draft"
        )
        db.add(db_template)
        db.flush()
        
        # Create variables
        for var in template.variables:
            db_var = models.TemplateVariable(
                template_id=db_template.id,
                name=var.name,
                description=var.description,
                variable_type=var.variable_type,
                default_value=var.default_value,
                options=var.options,
                required=var.required
            )
            db.add(db_var)
        
        db.commit()
        db.refresh(db_template)
        return db_template
    
    @staticmethod
    def update_template(db: Session, template_id: int, update: schemas.TemplateUpdate, user_id: int) -> models.Template:
        """Update template and create new version if config changed"""
        db_template = db.query(models.Template).filter(
            models.Template.id == template_id,
            models.Template.author_id == user_id
        ).first()
        
        if not db_template:
            raise ValueError("Template not found or access denied")
        
        # If config changed, create new version
        if update.config and update.config != db_template.config:
            change_type = TemplateService.detect_change_type(db_template.config, update.config)
            new_version = TemplateService.get_next_version(db_template.version, change_type)
            
            # Create new version entry
            new_template = models.Template(
                name=update.name or db_template.name,
                description=update.description or db_template.description,
                version=new_version,
                config=update.config,
                parent_version_id=db_template.id,
                author_id=user_id,
                visibility=update.visibility or db_template.visibility,
                role_access=update.role_access or db_template.role_access,
                category=update.category or db_template.category,
                tags=update.tags or db_template.tags,
                status=db_template.status
            )
            db.add(new_template)
            db.commit()
            db.refresh(new_template)
            return new_template
        else:
            # Update metadata only
            if update.name:
                db_template.name = update.name
            if update.description:
                db_template.description = update.description
            if update.visibility:
                db_template.visibility = update.visibility
            if update.role_access:
                db_template.role_access = update.role_access
            if update.category:
                db_template.category = update.category
            if update.tags:
                db_template.tags = update.tags
            
            db_template.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(db_template)
            return db_template
    
    @staticmethod
    def publish_template(db: Session, template_id: int, user_id: int) -> models.Template:
        """Publish a template making it available in marketplace"""
        db_template = db.query(models.Template).filter(
            models.Template.id == template_id,
            models.Template.author_id == user_id
        ).first()
        
        if not db_template:
            raise ValueError("Template not found or access denied")
        
        if db_template.status != "draft":
            raise ValueError("Only draft templates can be published")
        
        db_template.status = "published"
        db_template.published_at = datetime.utcnow()
        db.commit()
        db.refresh(db_template)
        return db_template
    
    @staticmethod
    def search_templates(db: Session, params: schemas.TemplateSearchParams) -> tuple[List[models.Template], int]:
        """Search templates with filters"""
        query = db.query(models.Template).filter(models.Template.status == params.status)
        
        # Text search
        if params.query:
            search_pattern = f"%{params.query}%"
            query = query.filter(
                or_(
                    models.Template.name.ilike(search_pattern),
                    models.Template.description.ilike(search_pattern)
                )
            )
        
        # Category filter
        if params.category:
            query = query.filter(models.Template.category == params.category)
        
        # Tags filter (any tag matches)
        if params.tags:
            query = query.filter(
                or_(*[models.Template.tags.contains([tag]) for tag in params.tags])
            )
        
        # Rating filter
        if params.min_rating > 0:
            query = query.filter(models.Template.rating >= params.min_rating)
        
        # Total count
        total = query.count()
        
        # Sorting
        if params.sort_by == "usage_count":
            sort_column = models.Template.usage_count
        elif params.sort_by == "rating":
            sort_column = models.Template.rating
        else:
            sort_column = models.Template.created_at
        
        if params.order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(sort_column)
        
        # Pagination
        templates = query.offset(params.offset).limit(params.limit).all()
        
        return templates, total
    
    @staticmethod
    def get_template_versions(db: Session, template_id: int) -> List[models.Template]:
        """Get all versions of a template"""
        # Get the template
        template = db.query(models.Template).filter(models.Template.id == template_id).first()
        if not template:
            return []
        
        versions = [template]
        
        # Get all children versions
        def get_children(parent_id):
            children = db.query(models.Template).filter(
                models.Template.parent_version_id == parent_id
            ).all()
            for child in children:
                versions.append(child)
                get_children(child.id)
        
        get_children(template_id)
        
        # Sort by version
        versions.sort(key=lambda t: semver.VersionInfo.parse(t.version), reverse=True)
        return versions
    
    @staticmethod
    def instantiate_template(db: Session, template_id: int, dashboard_data: schemas.DashboardCreate, user_id: int) -> models.Dashboard:
        """Create a dashboard from a template"""
        template = db.query(models.Template).filter(models.Template.id == template_id).first()
        if not template:
            raise ValueError("Template not found")
        
        if template.status != "published":
            raise ValueError("Only published templates can be instantiated")
        
        # Substitute variables
        config = TemplateService.substitute_variables(template.config, dashboard_data.variable_values)
        
        # Create dashboard
        dashboard = models.Dashboard(
            name=dashboard_data.name,
            config=config,
            owner_id=user_id,
            template_id=template_id,
            template_version=template.version
        )
        db.add(dashboard)
        
        # Increment usage count
        template.usage_count += 1
        
        db.commit()
        db.refresh(dashboard)
        return dashboard
    
    @staticmethod
    def rate_template(db: Session, template_id: int, user_id: int, rating_data: schemas.TemplateRatingCreate) -> models.TemplateRating:
        """Rate a template"""
        # Check if user already rated
        existing = db.query(models.TemplateRating).filter(
            models.TemplateRating.template_id == template_id,
            models.TemplateRating.user_id == user_id
        ).first()
        
        if existing:
            existing.rating = rating_data.rating
            existing.review = rating_data.review
            db_rating = existing
        else:
            db_rating = models.TemplateRating(
                template_id=template_id,
                user_id=user_id,
                rating=rating_data.rating,
                review=rating_data.review
            )
            db.add(db_rating)
        
        # Flush to ensure the rating is in the database before calculating average
        db.flush()
        
        # Update template rating
        avg_rating = db.query(func.avg(models.TemplateRating.rating)).filter(
            models.TemplateRating.template_id == template_id
        ).scalar()
        
        rating_count = db.query(func.count(models.TemplateRating.id)).filter(
            models.TemplateRating.template_id == template_id
        ).scalar()
        
        template = db.query(models.Template).filter(models.Template.id == template_id).first()
        if template:
            template.rating = int(avg_rating or 0)
            template.rating_count = rating_count or 0
        
        db.commit()
        db.refresh(db_rating)
        return db_rating
