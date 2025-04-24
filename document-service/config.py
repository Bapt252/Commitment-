import os
from typing import Optional, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    # Paramètres d'application
    APP_NAME: str = "NexTen Document Service"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Service de gestion des documents pour NexTen"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    PORT: int = 5000

    # Paramètres PostgreSQL
    POSTGRES_USER: str = Field(..., env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(..., env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field(..., env="POSTGRES_DB")
    POSTGRES_HOST: str = Field(..., env="POSTGRES_HOST")
    POSTGRES_PORT: int = 5432
    DATABASE_URL: Optional[str] = None

    @validator("DATABASE_URL", pre=True)
    def assemble_db_url(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if v:
            return v
        return f"postgresql://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_HOST')}:{values.get('POSTGRES_PORT')}/{values.get('POSTGRES_DB')}"

    # Paramètres Redis
    REDIS_HOST: str = Field(..., env="REDIS_HOST")
    REDIS_PORT: int = Field(..., env="REDIS_PORT")
    REDIS_DB: int = 0
    REDIS_URL: Optional[str] = None

    @validator("REDIS_URL", pre=True)
    def assemble_redis_url(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if v:
            return v
        return f"redis://{values.get('REDIS_HOST')}:{values.get('REDIS_PORT')}/{values.get('REDIS_DB')}"

    # Paramètres MinIO
    MINIO_ENDPOINT: str = Field(..., env="MINIO_ENDPOINT")
    MINIO_ACCESS_KEY: str = Field(..., env="MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY: str = Field(..., env="MINIO_SECRET_KEY")
    MINIO_SECURE: bool = False
    DOCUMENT_BUCKET: str = Field(..., env="DOCUMENT_BUCKET")
    ARCHIVE_BUCKET: str = Field(..., env="ARCHIVE_BUCKET")

    # Sécurité et JWT
    JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field(..., env="JWT_ALGORITHM")
    JWT_AUDIENCE: str = Field(..., env="JWT_AUDIENCE")
    JWT_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Paramètres ClamAV
    CLAMAV_HOST: str = Field(..., env="CLAMAV_HOST")
    CLAMAV_PORT: int = Field(..., env="CLAMAV_PORT")
    
    # Paramètres de gestion des documents
    MAX_UPLOAD_SIZE: int = 20 * 1024 * 1024  # 20 Mo par défaut
    DEFAULT_DOCUMENT_EXPIRY_DAYS: int = 365  # 1 an par défaut
    PRESIGNED_URL_EXPIRE_SECONDS: int = 300  # 5 minutes par défaut
    ALLOWED_DOCUMENT_TYPES: list = ["cv", "cover_letter", "job_description"]
    ALLOWED_MIME_TYPES: list = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
        "application/rtf",
        "application/vnd.oasis.opendocument.text",
        "image/jpeg",
        "image/png"
    ]
    
    # Redis Queue
    REDIS_JOB_TIMEOUT: int = 3600  # 1 heure
    REDIS_JOB_TTL: int = 86400  # 1 jour
    
    # Integration Services
    CV_PARSER_SERVICE_URL: Optional[str] = "http://cv-parser:5000"
    MATCHING_SERVICE_URL: Optional[str] = "http://matching-api:5000"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Créer une instance unique des paramètres
settings = Settings()
