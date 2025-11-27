import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.template import Base, Template, ReportFormat
from app.services.template_service import TemplateService

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_create_template(db_session):
    template = TemplateService.create_template(
        db_session,
        name="Test Template",
        content="<h1>{{ title }}</h1>"
    )
    assert template.id is not None
    assert template.name == "Test Template"
    assert "title" in template.variables

def test_extract_variables():
    content = "Hello {{ name }}, today is {{ date }}"
    variables = TemplateService.extract_variables(content)
    assert "name" in variables
    assert "date" in variables

def test_validate_template():
    valid, msg = TemplateService.validate_template("<h1>{{ title }}</h1>")
    assert valid is True
    
    valid, msg = TemplateService.validate_template("<h1>{{ unclosed }</h1>")
    assert valid is False

def test_render_template(db_session):
    template = TemplateService.create_template(
        db_session,
        name="Test",
        content="<h1>{{ title }}</h1>"
    )
    rendered = TemplateService.render_template(template, {"title": "Hello World"})
    assert "Hello World" in rendered
