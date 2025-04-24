# CV Parser Service - Configuration

import os
from pydantic import BaseSettings, Field
from typing import Optional, Dict, Any, List

class Settings(BaseSettings):
    """Configuration centralisée de l'application"""
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = Field(default=False, env="DEBUG")
    PROJECT_NAME: str = "cv-parser-service"
    PORT: int = Field(default=5000, env="PORT")
    
    # Sécurité
    REQUIRE_API_KEY: bool = Field(default=False, env="REQUIRE_API_KEY")
    API_KEY: str = Field(default="", env="API_KEY")
    RATE_LIMIT_ENABLED: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    
    # Redis Settings
    REDIS_HOST: str = Field(default="redis", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    REDIS_PASSWORD: str = Field(default="", env="REDIS_PASSWORD")
    
    # MinIO Settings
    MINIO_ENDPOINT: str = Field(default="storage:9000", env="MINIO_ENDPOINT")
    MINIO_ACCESS_KEY: str = Field(default="minioadmin", env="MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY: str = Field(default="minioadmin", env="MINIO_SECRET_KEY")
    MINIO_BUCKET_NAME: str = Field(default="cv-files", env="MINIO_BUCKET_NAME")
    MINIO_SECURE: bool = Field(default=False, env="MINIO_SECURE")
    
    # OpenAI API Settings
    OPENAI_API_KEY: str = Field(default="", env=["OPENAI", "OPENAI_API_KEY"])  # Accepte OPENAI ou OPENAI_API_KEY
    OPENAI_MODEL: str = Field(default="gpt-4o-mini", env="OPENAI_MODEL")
    
    # RQ Settings
    DEFAULT_TIMEOUT: int = Field(default=300, env="DEFAULT_TIMEOUT")  # 5 minutes
    RESULT_TTL: int = Field(default=86400, env="RESULT_TTL")  # 24 heures
    FAILURE_TTL: int = Field(default=86400, env="FAILURE_TTL")  # 24 heures
    JOB_TTL: int = Field(default=3600, env="JOB_TTL")  # 1 heure
    MAX_RETRIES: int = Field(default=3, env="MAX_RETRIES")
    
    # Circuit breaker settings
    CIRCUIT_BREAKER_ENABLED: bool = Field(default=True, env="CIRCUIT_BREAKER_ENABLED")
    CIRCUIT_BREAKER_THRESHOLD: int = Field(default=5, env="CIRCUIT_BREAKER_THRESHOLD")
    CIRCUIT_BREAKER_TIMEOUT: int = Field(default=60, env="CIRCUIT_BREAKER_TIMEOUT")  # secondes
    
    # Fichiers temporaires
    TEMP_DIR: str = Field(default="/tmp", env="TEMP_DIR")
    CLEANUP_TEMP_FILES: bool = Field(default=True, env="CLEANUP_TEMP_FILES")
    
    # Validation des fichiers
    MAX_CONTENT_LENGTH: int = Field(default=10 * 1024 * 1024, env="MAX_CONTENT_LENGTH")  # 10MB
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=[".pdf", ".docx", ".doc", ".txt", ".rtf"],
        env="ALLOWED_EXTENSIONS"
    )
    
    # Storage strategy
    USE_MINIO_FOR_FILES: bool = Field(default=True, env="USE_MINIO_FOR_FILES")
    STORE_RESULTS_IN_REDIS: bool = Field(default=True, env="STORE_RESULTS_IN_REDIS")
    REDIS_RESULT_TTL: int = Field(default=3600, env="REDIS_RESULT_TTL")  # 1 heure
    
    # PostgreSQL config (pour stockage résultat à long terme)
    STORE_RESULTS_IN_POSTGRES: bool = Field(default=False, env="STORE_RESULTS_IN_POSTGRES")
    DATABASE_URL: Optional[str] = Field(default=None, env="DATABASE_URL")
    
    # Multi-tier storage
    LARGE_RESULT_THRESHOLD: int = Field(default=100 * 1024, env="LARGE_RESULT_THRESHOLD")  # 100KB
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")
    LOG_FILE: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # Webhook settings
    WEBHOOK_TIMEOUT: int = Field(default=10, env="WEBHOOK_TIMEOUT")  # secondes
    WEBHOOK_MAX_RETRIES: int = Field(default=3, env="WEBHOOK_MAX_RETRIES")

    class Config:
        env_file = ".env"
        case_sensitive = True

# Créer une instance globale de la configuration
settings = Settings()
