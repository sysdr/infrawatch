from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: str
    role: str = "viewer"

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TemplateVariableBase(BaseModel):
    name: str
    description: Optional[str] = None
    variable_type: str = "string"
    default_value: Optional[str] = None
    options: List[str] = []
    required: bool = True

class TemplateVariableCreate(TemplateVariableBase):
    pass

class TemplateVariable(TemplateVariableBase):
    id: int
    template_id: int
    model_config = ConfigDict(from_attributes=True)

class TemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    config: Dict[str, Any]
    visibility: str = "private"
    role_access: List[str] = []
    category: Optional[str] = None
    tags: List[str] = []

class TemplateCreate(TemplateBase):
    variables: List[TemplateVariableCreate] = []

class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    visibility: Optional[str] = None
    role_access: Optional[List[str]] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None

class Template(TemplateBase):
    id: int
    version: str
    parent_version_id: Optional[int] = None
    author_id: int
    status: str
    usage_count: int
    rating: int
    rating_count: int
    preview_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    variables: List[TemplateVariable] = []
    model_config = ConfigDict(from_attributes=True)

class TemplateListItem(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    version: str
    category: Optional[str] = None
    tags: List[str]
    status: str
    usage_count: int
    rating: int
    rating_count: int
    author_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class DashboardCreate(BaseModel):
    name: str
    template_id: Optional[int] = None
    variable_values: Dict[str, Any] = {}

class Dashboard(BaseModel):
    id: int
    name: str
    config: Dict[str, Any]
    owner_id: int
    template_id: Optional[int] = None
    template_version: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TemplateRatingCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    review: Optional[str] = None

class TemplateRating(BaseModel):
    id: int
    template_id: int
    user_id: int
    rating: int
    review: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TemplateSearchParams(BaseModel):
    query: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = []
    status: str = "published"
    min_rating: int = 0
    sort_by: str = "created_at"  # created_at, usage_count, rating
    order: str = "desc"
    limit: int = 20
    offset: int = 0
