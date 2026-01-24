from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5433/infradb"
    redis_url: str = "redis://localhost:6379"
    secret_key: str = ""  # Set via environment variable SECRET_KEY
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    
    # Cloud provider credentials - set via environment variables
    aws_access_key: str = ""  # Set via AWS_ACCESS_KEY_ID
    aws_secret_key: str = ""  # Set via AWS_SECRET_ACCESS_KEY
    aws_region: str = "us-east-1"
    
    class Config:
        env_file = ".env"

settings = Settings()
