from fastapi import APIRouter, Depends
from app.models.template import TemplateRenderRequest
from app.services.template_service import TemplateService

router = APIRouter()

def get_template_service():
    return TemplateService()

@router.get("/sample-data")
async def get_sample_data():
    """Get sample test data for templates"""
    return {
        "welcome_user": {
            "user": {
                "first_name": "Sarah",
                "last_name": "Johnson",
                "email": "sarah.johnson@example.com"
            },
            "app_name": "NotifyHub",
            "verification_link": "https://app.notifyhub.com/verify/abc123",
            "signup_date": "2024-01-15T10:30:00Z"
        },
        "password_reset": {
            "user": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com"
            },
            "app_name": "NotifyHub",
            "reset_link": "https://app.notifyhub.com/reset/xyz789",
            "expiry_time": "2024-01-16T10:30:00Z"
        }
    }

@router.post("/render-all")
async def test_render_all(service: TemplateService = Depends(get_template_service)):
    """Test render all templates with sample data"""
    await service.initialize()
    
    sample_data = await get_sample_data()
    results = []
    
    for template in service.get_templates():
        template_data = sample_data.get(template.id, {})
        
        for format_config in template.formats:
            for locale in template.locales:
                request = TemplateRenderRequest(
                    template_id=template.id,
                    format_type=format_config.format_type,
                    locale=locale,
                    context=template_data,
                    test_mode=True
                )
                
                result = await service.render_template(request)
                results.append({
                    "template_id": template.id,
                    "format": format_config.format_type,
                    "locale": locale,
                    "success": result.success,
                    "error": result.error,
                    "content_length": len(result.content) if result.content else 0,
                    "warnings": result.validation_warnings
                })
    
    return {"test_results": results}
