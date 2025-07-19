from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Hirify - AI-Powered Job Matching Platform"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Intelligent resume parsing and job matching system"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    ALGORITHM: str = "HS256"
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 24
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = 24
    
    # Performance monitoring
    ENABLE_MEMORY_TRACKING: bool = False
    SLOW_REQUEST_THRESHOLD: float = 2.0
    MEMORY_THRESHOLD: int = 100 * 1024 * 1024  # 100MB
    HIGH_CPU_THRESHOLD: float = 80.0
    HIGH_MEMORY_THRESHOLD: float = 80.0
    MAX_DB_CONNECTIONS: int = 100
    MEMORY_LEAK_THRESHOLD: int = 10 * 1024 * 1024  # 10MB
    SLOW_OPERATION_THRESHOLD: float = 5.0
    MONITORING_INTERVAL: int = 60
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/hirify"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # File Storage
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["pdf", "doc", "docx"]
    
    # NLP Settings
    SPACY_MODEL: str = "en_core_web_sm"
    BERT_MODEL: str = "bert-base-uncased"
    SIMILARITY_THRESHOLD: float = 0.5
    
    # Email settings (for password reset)
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: Optional[str] = None
    
    # Performance settings
    ENABLE_CACHING: bool = True
    CACHE_TTL: int = 3600
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
