from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Infrastructure Management API"
    database_url: str = "sqlite:///./versioning.db"
    debug: bool = True
    class Config:
        env_file = ".env"

settings = Settings()
