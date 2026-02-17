from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import Dict, Any
import pandas as pd

class TemplateEngine:
    """Manages report templates with Jinja2"""
    
    def __init__(self):
        self.env = Environment(
            loader=FileSystemLoader('app/templates/reports'),
            autoescape=select_autoescape(['html', 'xml'])
        )
        self._register_filters()
    
    def _register_filters(self):
        """Register custom Jinja2 filters"""
        self.env.filters['format_number'] = lambda x: f"{x:,.2f}"
        self.env.filters['format_percent'] = lambda x: f"{x:.1f}%"
        self.env.filters['format_date'] = lambda x: x.strftime("%Y-%m-%d") if hasattr(x, 'strftime') else str(x)
    
    def render(self, template_name: str, data: Dict[str, Any]) -> str:
        """Render template with data"""
        template = self.env.get_template(template_name)
        return template.render(**data)
    
    def get_template_structure(self, layout_config: Dict[str, Any]) -> Dict[str, Any]:
        """Parse layout configuration into structured sections"""
        sections = layout_config.get("sections", [])
        
        structure = {
            "title": layout_config.get("title", "Report"),
            "sections": []
        }
        
        for section in sections:
            structure["sections"].append({
                "title": section.get("title", ""),
                "type": section.get("type", "table"),  # table, chart, text
                "data_source": section.get("data_source", ""),
                "options": section.get("options", {})
            })
        
        return structure
