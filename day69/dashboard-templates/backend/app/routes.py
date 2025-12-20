from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from . import models, schemas, services
from .database import get_db

router = APIRouter()

# Mock authentication - in production use proper JWT
def get_current_user(db: Session = Depends(get_db)) -> models.User:
    user = db.query(models.User).first()
    if not user:
        # Create default user
        user = models.User(username="admin", email="admin@example.com", role="admin")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

@router.post("/templates", response_model=schemas.Template, status_code=201)
def create_template(
    template: schemas.TemplateCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Create a new template"""
    return services.TemplateService.create_template(db, template, current_user.id)

@router.get("/templates", response_model=dict)
def search_templates(
    query: Optional[str] = None,
    category: Optional[str] = None,
    tags: Optional[str] = None,
    status: str = "published",
    min_rating: int = 0,
    sort_by: str = "created_at",
    order: str = "desc",
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Search templates with filters"""
    tag_list = tags.split(",") if tags else []
    params = schemas.TemplateSearchParams(
        query=query,
        category=category,
        tags=tag_list,
        status=status,
        min_rating=min_rating,
        sort_by=sort_by,
        order=order,
        limit=limit,
        offset=offset
    )
    templates, total = services.TemplateService.search_templates(db, params)
    return {
        "templates": [schemas.TemplateListItem.model_validate(t) for t in templates],
        "total": total,
        "limit": limit,
        "offset": offset
    }

@router.get("/templates/{template_id}", response_model=schemas.Template)
def get_template(template_id: int, db: Session = Depends(get_db)):
    """Get template by ID"""
    template = db.query(models.Template).filter(models.Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.put("/templates/{template_id}", response_model=schemas.Template)
def update_template(
    template_id: int,
    update: schemas.TemplateUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Update template (creates new version if config changed)"""
    try:
        return services.TemplateService.update_template(db, template_id, update, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.post("/templates/{template_id}/publish", response_model=schemas.Template)
def publish_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Publish a template"""
    try:
        return services.TemplateService.publish_template(db, template_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/templates/{template_id}/versions", response_model=List[schemas.TemplateListItem])
def get_template_versions(template_id: int, db: Session = Depends(get_db)):
    """Get all versions of a template"""
    versions = services.TemplateService.get_template_versions(db, template_id)
    return [schemas.TemplateListItem.model_validate(v) for v in versions]

@router.post("/templates/{template_id}/instantiate", response_model=schemas.Dashboard)
def instantiate_template(
    template_id: int,
    dashboard_data: schemas.DashboardCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Create a dashboard from template"""
    try:
        return services.TemplateService.instantiate_template(db, template_id, dashboard_data, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/templates/{template_id}/rate", response_model=schemas.TemplateRating)
def rate_template(
    template_id: int,
    rating: schemas.TemplateRatingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Rate a template"""
    return services.TemplateService.rate_template(db, template_id, current_user.id, rating)

@router.get("/dashboards", response_model=List[schemas.Dashboard])
def get_dashboards(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get user's dashboards"""
    dashboards = db.query(models.Dashboard).filter(
        models.Dashboard.owner_id == current_user.id
    ).all()
    return dashboards

@router.get("/categories", response_model=List[str])
def get_categories(db: Session = Depends(get_db)):
    """Get all template categories"""
    categories = db.query(models.Template.category).distinct().all()
    return [c[0] for c in categories if c[0]]

@router.get("/stats", response_model=dict)
def get_stats(db: Session = Depends(get_db)):
    """Get marketplace stats"""
    total_templates = db.query(models.Template).filter(
        models.Template.status == "published"
    ).count()
    
    total_dashboards = db.query(models.Dashboard).count()
    
    popular_templates = db.query(models.Template).filter(
        models.Template.status == "published"
    ).order_by(models.Template.usage_count.desc()).limit(5).all()
    
    return {
        "total_templates": total_templates,
        "total_dashboards": total_dashboards,
        "popular_templates": [
            {
                "id": t.id,
                "name": t.name,
                "usage_count": t.usage_count,
                "rating": t.rating
            }
            for t in popular_templates
        ]
    }
