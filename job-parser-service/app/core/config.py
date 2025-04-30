# Import des modules nécessaires
import os
from typing import Optional, Dict, Any, List
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Configuration globale du service de parsing de fiches de poste"""
    
    # Chemin de base pour les variables d'environnement (préfixe)
    # env_prefix = "JOB_PARSER_"
    
    # Configuration de l'API
    DEBUG: bool = Field(False, env="DEBUG")
    PORT: int = Field(5000, env="PORT")
    SERVICE_NAME: str = Field("job-parser", env="SERVICE_NAME")
    REQUIRE_API_KEY: bool = Field(False, env="REQUIRE_API_KEY")
    API_KEY: Optional[str] = Field(None, env="API_KEY")
    CORS_ORIGINS: List[str] = Field(["*"], env="CORS_ORIGINS")
    
    # Configuration de Redis
    REDIS_HOST: str = Field("redis", env="REDIS_HOST")
    REDIS_PORT: int = Field(6379, env="REDIS_PORT")
    REDIS_DB: int = Field(0, env="REDIS_DB")
    REDIS_PASSWORD: Optional[str] = Field(None, env="REDIS_PASSWORD")
    REDIS_RESULT_TTL: int = Field(3600, env="REDIS_RESULT_TTL")  # 1 heure
    STORE_RESULTS_IN_REDIS: bool = Field(True, env="STORE_RESULTS_IN_REDIS")
    
    # Configuration de MinIO/S3
    USE_MINIO_FOR_FILES: bool = Field(True, env="USE_MINIO_FOR_FILES")
    MINIO_ENDPOINT: str = Field("storage:9000", env="MINIO_ENDPOINT")
    MINIO_ACCESS_KEY: str = Field("minioadmin", env="MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY: str = Field("minioadmin", env="MINIO_SECRET_KEY")
    MINIO_SECURE: bool = Field(False, env="MINIO_SECURE")
    MINIO_BUCKET_NAME: str = Field("job-files", env="MINIO_BUCKET_NAME")
    
    # Chemin pour les fichiers temporaires
    TEMP_DIR: str = Field("/app/temp", env="TEMP_DIR")
    
    # Configuration des logs
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field("json", env="LOG_FORMAT")
    LOG_DIR: str = Field("/app/logs", env="LOG_DIR")
    
    # Configuration OpenAI
    OPENAI: Optional[str] = Field(None, env="OPENAI")
    OPENAI_MODEL: str = Field("gpt-4o-mini", env="OPENAI_MODEL")
    USE_MOCK_PARSER: bool = Field(False, env="USE_MOCK_PARSER")
    
    # Resilience settings
    CIRCUIT_BREAKER_ENABLED: bool = Field(True, env="CIRCUIT_BREAKER_ENABLED")
    MAX_RETRIES: int = Field(3, env="MAX_RETRIES")
    
    # Service matching
    MATCHING_API_URL: Optional[str] = Field(None, env="MATCHING_API_URL")
    
    class Config:
        # Emplacement du fichier .env si utilisé
        env_file = ".env"
        # Autoriser des variables extra non connues
        extra = "allow"
        # Validation silencieuse (pas d'erreur si variables manquantes)
        validate_assignment = True

# Création d'une instance de la configuration
settings = Settings()

# Créer les répertoires temporaires et logs s'ils n'existent pas
os.makedirs(settings.TEMP_DIR, exist_ok=True)
os.makedirs(settings.LOG_DIR, exist_ok=True)
