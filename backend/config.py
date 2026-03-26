import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "NeuroScan AI"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Security
    JWT_SECRET: str = "default-secret-key-change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # Database
    DATABASE_URL: str = "sqlite:///database.db"
    
    # File Upload
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: List[str] = ["png", "jpg", "jpeg"]
    
    # CORS
    CORS_ORIGINS: str = "*"
    
    # Model
    MODEL_PATH: str = "models/efficientnet_b0_best.h5"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()