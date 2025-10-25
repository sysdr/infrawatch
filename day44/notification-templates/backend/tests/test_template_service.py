import pytest
import pytest_asyncio
from app.services.template_service import TemplateService
from app.models.template import TemplateRenderRequest

@pytest.fixture
async def template_service():
    service = TemplateService()
    await service.initialize()
    return service

@pytest.mark.asyncio
async def test_template_loading(template_service):
    """Test that templates are loaded correctly"""
    templates = template_service.get_templates()
    assert len(templates) > 0
    
    welcome_template = template_service.get_template("welcome_user")
    assert welcome_template is not None
    assert welcome_template.name == "Welcome New User"

@pytest.mark.asyncio
async def test_template_rendering(template_service):
    """Test template rendering with context"""
    request = TemplateRenderRequest(
        template_id="welcome_user",
        format_type="email",
        locale="en",
        context={
            "user": {"first_name": "John", "email": "john@example.com"},
            "app_name": "TestApp",
            "verification_link": "https://test.com/verify/123",
            "signup_date": "2024-01-15T10:30:00Z"
        }
    )
    
    result = await template_service.render_template(request)
    assert result.success is True
    assert "John" in result.content
    assert "TestApp" in result.content
    assert result.subject is not None

@pytest.mark.asyncio
async def test_localization(template_service):
    """Test localized template rendering"""
    context = {
        "user": {"first_name": "María", "email": "maria@example.com"},
        "app_name": "TestApp",
        "verification_link": "https://test.com/verify/123",
        "signup_date": "2024-01-15T10:30:00Z"
    }
    
    # Test English
    en_request = TemplateRenderRequest(
        template_id="welcome_user", format_type="email", locale="en", context=context
    )
    en_result = await template_service.render_template(en_request)
    
    # Test Spanish
    es_request = TemplateRenderRequest(
        template_id="welcome_user", format_type="email", locale="es", context=context
    )
    es_result = await template_service.render_template(es_request)
    
    assert en_result.success is True
    assert es_result.success is True
    assert "Welcome" in en_result.content
    assert "Bienvenido" in es_result.content

@pytest.mark.asyncio
async def test_sms_character_limit(template_service):
    """Test SMS character limit warnings"""
    long_name = "VeryLongFirstNameThatExceedsNormalLength"
    context = {
        "user": {"first_name": long_name, "email": "test@example.com"},
        "app_name": "TestAppWithVeryLongName",
        "verification_link": "https://very-long-domain-name.com/verify/very-long-verification-token-123456789"
    }
    
    request = TemplateRenderRequest(
        template_id="welcome_user", format_type="sms", locale="en", context=context
    )
    
    result = await template_service.render_template(request)
    assert result.success is True
    # Should have character limit warning
    assert len(result.validation_warnings) > 0

@pytest.mark.asyncio
async def test_template_validation(template_service):
    """Test template validation"""
    result = await template_service.validate_template("welcome_user")
    assert result["valid"] is True
    
    # Test invalid template
    result = await template_service.validate_template("non_existent")
    assert result["valid"] is False

@pytest.mark.asyncio
async def test_missing_variables(template_service):
    """Test handling of missing variables"""
    request = TemplateRenderRequest(
        template_id="welcome_user",
        format_type="email",
        locale="en",
        context={"user": {"first_name": "John"}}  # Missing required variables
    )
    
    result = await template_service.render_template(request)
    # Should still render but may have undefined variables
    assert result.success is True
