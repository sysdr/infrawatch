from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Dict, Any
import math

from ..models.server_models import Server, Group
from ..schemas.server_schemas import ServerSearchRequest, ServerSearchResponse, ServerResponse

async def search_servers(db: Session, search_request: ServerSearchRequest) -> ServerSearchResponse:
    """Advanced server search with filtering and pagination"""
    
    query = db.query(Server)
    
    # Apply filters
    if search_request.filters:
        filter_conditions = []
        for filter_criteria in search_request.filters:
            condition = _build_filter_condition(filter_criteria)
            if condition is not None:
                filter_conditions.append(condition)
        
        if filter_conditions:
            query = query.filter(and_(*filter_conditions))
    
    # Apply sorting
    if search_request.sort:
        for sort_criteria in search_request.sort:
            field = getattr(Server, sort_criteria.field, None)
            if field:
                if sort_criteria.direction == "desc":
                    query = query.order_by(field.desc())
                else:
                    query = query.order_by(field.asc())
    else:
        query = query.order_by(Server.created_at.desc())
    
    # Count total results
    total = query.count()
    
    # Apply pagination
    offset = (search_request.page - 1) * search_request.page_size
    servers = query.offset(offset).limit(search_request.page_size).all()
    
    # Calculate pagination info
    total_pages = math.ceil(total / search_request.page_size)
    
    return ServerSearchResponse(
        servers=[ServerResponse.model_validate(server) for server in servers],
        total=total,
        page=search_request.page,
        page_size=search_request.page_size,
        total_pages=total_pages,
    )

def _build_filter_condition(filter_criteria):
    """Build SQLAlchemy filter condition from criteria"""
    field = getattr(Server, filter_criteria.field, None)
    if not field:
        return None
    
    operator = filter_criteria.operator
    value = filter_criteria.value
    
    if operator == "eq":
        return field == value
    elif operator == "ne":
        return field != value
    elif operator == "in":
        return field.in_(value)
    elif operator == "not_in":
        return ~field.in_(value)
    elif operator == "like":
        return field.like(f"%{value}%")
    elif operator == "gt":
        return field > value
    elif operator == "lt":
        return field < value
    elif operator == "gte":
        return field >= value
    elif operator == "lte":
        return field <= value
    
    return None
