from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/notifications"
    REDIS_URL: str = "redis://redis:6379/0"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    TWILIO_ACCOUNT_SID: str = "test_sid"
    TWILIO_AUTH_TOKEN: str = "test_token"
    TWILIO_FROM_NUMBER: str = "+1234567890"
    SLACK_WEBHOOK_URL: str = "https://hooks.slack.com/test"
    
    class Config:
        env_file = ".env"

settings = Settings()
