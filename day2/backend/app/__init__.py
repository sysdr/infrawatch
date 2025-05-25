from flask import Flask
from app.core.config import Config
from app.api.v1 import health_bp, infrastructure_bp

def create_app(config_class=Config):
    """Application factory pattern - enables testing and multiple configurations"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Register blueprints (modular architecture)
    app.register_blueprint(health_bp, url_prefix='/api/v1')
    app.register_blueprint(infrastructure_bp, url_prefix='/api/v1')
    
    return app
