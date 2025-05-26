"""
Configuration du service de matching.
Définit les paramètres de configuration avec valeurs par défaut et chargement depuis les variables d'environnement.
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from enum import Enum

class QueuePriority(str, Enum):
    """Priorités de file d'attente disponibles"""
    HIGH = "matching_high"
    STANDARD = "matching_standard"
    BULK = "matching_bulk"
    FAILED = "matching_failed"  # Queue pour les jobs échoués (dead letter queue)

class Settings(BaseSettings):
    """
    Configuration globale du service avec valeurs par défaut
    Pydantic chargera automatiquement les variables d'environnement correspondantes
    """
    # Service
    SERVICE_NAME: str = "matching-service"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    PORT: int = 5000
    
    # FastAPI
    API_PORT: int = 5000
    CORS_ORIGINS: List[str] = ["*"]
    
    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_JOB_TIMEOUT: int = 3600     # Timeout d'1 heure pour les jobs
    REDIS_JOB_TTL: int = 86400        # TTL pour les résultats de job (1 jour)
    REDIS_URL: str = ""
    
    # PostgreSQL
    DATABASE_URL: str = "postgresql://postgres:postgres@postgres:5432/nexten"
    
    # MinIO
    MINIO_ENDPOINT: str = "storage:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET_NAME: str = "matching-results"
    MINIO_SECURE: bool = False
    
    # Google Maps API
    GOOGLE_MAPS_API_KEY: str = ""
    
    # Queues
    QUEUE_NAMES: List[str] = [
        QueuePriority.HIGH,
        QueuePriority.STANDARD,
        QueuePriority.BULK,
        QueuePriority.FAILED
    ]
    QUEUE_DEFAULT: str = QueuePriority.STANDARD
    
    # Webhook
    WEBHOOK_SECRET: str = "your-secret-key"
    WEBHOOK_RETRY_COUNT: int = 3
    WEBHOOK_RETRY_DELAY: int = 5  # secondes
    
    # Worker settings
    WORKER_CONCURRENCY: int = int(os.cpu_count() or 4)
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 60  # secondes
    
    # Circuit Breaker
    CIRCUIT_BREAKER_ENABLED: bool = True
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 5
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT: int = 30  # secondes
    
    # Configuration de l'URL Redis
    def __init__(self, **data):
        super().__init__(**data)
        password_part = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        self.REDIS_URL = f"redis://{password_part}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    class Config:
        env_file = ".env"
        case_sensitive = True

# Instanciation de la configuration
settings = Settings()
