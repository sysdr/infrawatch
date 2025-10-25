import os
import json
import aiofiles
from jinja2 import Environment, FileSystemLoader, Template as JinjaTemplate, meta
from babel import Locale, dates, numbers
from typing import Dict, List, Optional, Any
from app.models.template import Template, TemplateRenderRequest, TemplateRenderResponse
from datetime import datetime
import re

class TemplateService:
    def __init__(self):
        self.templates_dir = "templates"
        self.locales_dir = "locales"
        self.templates_cache: Dict[str, Template] = {}
        self.jinja_env = Environment(
            loader=FileSystemLoader([self.templates_dir, self.locales_dir]),
            autoescape=True
        )
        self._setup_filters()
    
    def _setup_filters(self):
        """Setup custom Jinja2 filters for date formatting, etc."""
        def format_datetime(value, format='medium', locale='en'):
            if isinstance(value, str):
                value = datetime.fromisoformat(value.replace('Z', '+00:00'))
            locale_obj = Locale(locale)
            return dates.format_datetime(value, format, locale=locale_obj)
        
        def format_currency(value, currency='USD', locale='en'):
            locale_obj = Locale(locale)
            return numbers.format_currency(value, currency, locale=locale_obj)
        
        def truncate_smart(value, length=100, suffix='...'):
            if len(value) <= length:
                return value
            return value[:length-len(suffix)].rsplit(' ', 1)[0] + suffix
        
        self.jinja_env.filters['datetime'] = format_datetime
        self.jinja_env.filters['currency'] = format_currency
        self.jinja_env.filters['truncate_smart'] = truncate_smart
    
    async def initialize(self):
        """Initialize service and load templates"""
        await self.load_templates()
    
    async def load_templates(self):
        """Load all templates from templates directory"""
        template_configs = await self._discover_templates()
        for config in template_configs:
            template = Template(**config)
            self.templates_cache[template.id] = template
    
    async def _discover_templates(self) -> List[Dict]:
        """Discover and load template configurations"""
        configs = []
        
        # Sample templates for demo
        configs.extend([
            {
                "id": "welcome_user",
                "name": "Welcome New User",
                "description": "Welcome message for new user registration",
                "category": "user_onboarding",
                "formats": [
                    {"format_type": "email", "template_path": "email/welcome.html", "subject_template": "Welcome to {{app_name}}, {{user.first_name}}!"},
                    {"format_type": "sms", "template_path": "sms/welcome.txt", "character_limit": 160},
                    {"format_type": "push", "template_path": "push/welcome.json"}
                ],
                "variables": [
                    {"name": "user.first_name", "type": "string", "required": True, "description": "User's first name"},
                    {"name": "user.email", "type": "string", "required": True, "description": "User's email address"},
                    {"name": "app_name", "type": "string", "required": True, "description": "Application name"},
                    {"name": "verification_link", "type": "string", "required": True, "description": "Email verification link"},
                    {"name": "signup_date", "type": "date", "required": False, "description": "User registration date"}
                ],
                "locales": ["en", "es", "fr"]
            },
            {
                "id": "password_reset",
                "name": "Password Reset",
                "description": "Password reset notification",
                "category": "security",
                "formats": [
                    {"format_type": "email", "template_path": "email/password_reset.html", "subject_template": "Reset your password - {{app_name}}"},
                    {"format_type": "sms", "template_path": "sms/password_reset.txt", "character_limit": 160}
                ],
                "variables": [
                    {"name": "user.first_name", "type": "string", "required": True},
                    {"name": "reset_link", "type": "string", "required": True},
                    {"name": "expiry_time", "type": "date", "required": True},
                    {"name": "app_name", "type": "string", "required": True}
                ],
                "locales": ["en", "es", "fr"]
            }
        ])
        
        return configs
    
    async def render_template(self, request: TemplateRenderRequest) -> TemplateRenderResponse:
        """Render template with provided context"""
        try:
            template = self.templates_cache.get(request.template_id)
            if not template:
                return TemplateRenderResponse(
                    success=False,
                    format_type=request.format_type,
                    locale=request.locale,
                    variables_used=[],
                    error=f"Template {request.template_id} not found"
                )
            
            # Find format
            format_config = next((f for f in template.formats if f.format_type == request.format_type), None)
            if not format_config:
                return TemplateRenderResponse(
                    success=False,
                    format_type=request.format_type,
                    locale=request.locale,
                    variables_used=[],
                    error=f"Format {request.format_type} not supported for template {request.template_id}"
                )
            
            # Load and render template
            template_path = self._get_localized_template_path(format_config.template_path, request.locale)
            template_content = await self._load_template_file(template_path)
            
            if not template_content:
                return TemplateRenderResponse(
                    success=False,
                    format_type=request.format_type,
                    locale=request.locale,
                    variables_used=[],
                    error=f"Template file not found: {template_path}"
                )
            
            # Enhance context with locale and formatting helpers
            enhanced_context = {
                **request.context,
                'locale': request.locale,
                'now': datetime.now()
            }
            
            # Render content
            jinja_template = self.jinja_env.from_string(template_content)
            rendered_content = jinja_template.render(**enhanced_context)
            
            # Render subject if email
            rendered_subject = None
            if format_config.subject_template and request.format_type == 'email':
                subject_template = self.jinja_env.from_string(format_config.subject_template)
                rendered_subject = subject_template.render(**enhanced_context)
            
            # Get variables used
            variables_used = list(meta.find_undeclared_variables(self.jinja_env.parse(template_content)))
            
            # Validate character limit for SMS
            warnings = []
            if format_config.character_limit and len(rendered_content) > format_config.character_limit:
                warnings.append(f"Content exceeds character limit ({len(rendered_content)}/{format_config.character_limit})")
            
            return TemplateRenderResponse(
                success=True,
                content=rendered_content,
                subject=rendered_subject,
                format_type=request.format_type,
                locale=request.locale,
                variables_used=variables_used,
                validation_warnings=warnings
            )
            
        except Exception as e:
            return TemplateRenderResponse(
                success=False,
                format_type=request.format_type,
                locale=request.locale,
                variables_used=[],
                error=str(e)
            )
    
    def _get_localized_template_path(self, base_path: str, locale: str) -> str:
        """Get localized template path"""
        if locale == 'en':
            return base_path
        
        path_parts = base_path.split('/')
        filename = path_parts[-1]
        name, ext = filename.rsplit('.', 1)
        localized_filename = f"{name}_{locale}.{ext}"
        path_parts[-1] = localized_filename
        
        return '/'.join(path_parts)
    
    async def _load_template_file(self, template_path: str) -> Optional[str]:
        """Load template file content"""
        full_path = os.path.join(self.templates_dir, template_path)
        try:
            async with aiofiles.open(full_path, 'r', encoding='utf-8') as f:
                return await f.read()
        except FileNotFoundError:
            # Try fallback to English
            if '_' in template_path:
                fallback_path = template_path.split('_')[0] + '.' + template_path.split('.')[-1]
                return await self._load_template_file(fallback_path)
            return None
    
    async def validate_template(self, template_id: str) -> Dict[str, Any]:
        """Validate template syntax and completeness"""
        template = self.templates_cache.get(template_id)
        if not template:
            return {"valid": False, "errors": ["Template not found"]}
        
        errors = []
        warnings = []
        
        for format_config in template.formats:
            for locale in template.locales:
                template_path = self._get_localized_template_path(format_config.template_path, locale)
                content = await self._load_template_file(template_path)
                
                if not content:
                    errors.append(f"Missing template file: {template_path}")
                    continue
                
                try:
                    # Parse template to check syntax
                    jinja_template = self.jinja_env.from_string(content)
                    
                    # Check for undefined variables
                    template_vars = meta.find_undeclared_variables(self.jinja_env.parse(content))
                    declared_vars = {var.name for var in template.variables}
                    
                    undefined_vars = template_vars - declared_vars - {'locale', 'now'}
                    if undefined_vars:
                        warnings.append(f"Undefined variables in {template_path}: {list(undefined_vars)}")
                    
                except Exception as e:
                    errors.append(f"Syntax error in {template_path}: {str(e)}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def get_templates(self) -> List[Template]:
        """Get all templates"""
        return list(self.templates_cache.values())
    
    def get_template(self, template_id: str) -> Optional[Template]:
        """Get specific template"""
        return self.templates_cache.get(template_id)
