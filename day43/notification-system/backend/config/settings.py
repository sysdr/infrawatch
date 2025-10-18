from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/notifications"
    redis_url: str = "redis://localhost:6379/0"
    
    # Email
    sendgrid_api_key: Optional[str] = "demo_key"
    from_email: str = "alerts@company.com"
    
    # SMS
    twilio_account_sid: Optional[str] = "demo_sid"
    twilio_auth_token: Optional[str] = "demo_token"
    twilio_phone: str = "+1234567890"
    
    # Slack
    slack_bot_token: Optional[str] = "demo_token"
    slack_webhook_url: Optional[str] = "https://hooks.slack.com/demo"
    
    # Firebase (Push)
    firebase_credentials_path: Optional[str] = None
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()
