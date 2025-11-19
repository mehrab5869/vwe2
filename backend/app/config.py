"""
Application Configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://proxy_admin:proxy_pass@localhost:5432/proxy_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    ADMIN_SECRET_KEY: str = "change-this-in-production-min-32-chars-required"
    ENCRYPTION_KEY: str = "change-this-32-byte-key-in-production-use-32-chars"
    
    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()

