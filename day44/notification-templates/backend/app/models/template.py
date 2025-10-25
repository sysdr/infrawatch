from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime

class TemplateVariable(BaseModel):
    name: str
    type: str  # string, number, boolean, date, object
    required: bool = True
    default: Optional[Any] = None
    description: Optional[str] = None

class TemplateFormat(BaseModel):
    format_type: str  # email, sms, push, slack
    template_path: str
    subject_template: Optional[str] = None
    character_limit: Optional[int] = None

class Template(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    category: str
    formats: List[TemplateFormat]
    variables: List[TemplateVariable]
    locales: List[str] = ["en"]
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class TemplateRenderRequest(BaseModel):
    template_id: str
    format_type: str
    locale: str = "en"
    context: Dict[str, Any]
    test_mode: bool = False

class TemplateRenderResponse(BaseModel):
    success: bool
    content: Optional[str] = None
    subject: Optional[str] = None
    format_type: str
    locale: str
    variables_used: List[str]
    error: Optional[str] = None
    validation_warnings: List[str] = []
