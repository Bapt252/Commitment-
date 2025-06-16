"""
Configuration centralisée pour l'API Gateway SuperSmartMatch V2
Gestion des variables d'environnement et paramètres
"""

import os
from typing import List
from functools import lru_cache
from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """Configuration de l'application"""
    
    # Configuration générale
    APP_NAME: str = "SuperSmartMatch V2 API Gateway"
    VERSION: str = "2.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # Services endpoints
    CV_PARSER_URL: str = "http://cv-parser:5051"
    JOB_PARSER_URL: str = "http://job-parser:5053"
    MATCHING_SERVICE_URL: str = "http://matching-service:5060"
    
    # Sécurité JWT
    JWT_SECRET: str = "supersecure-jwt-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 24
    JWT_REFRESH_EXPIRE_DAYS: int = 7
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_BURST: int = 20
    
    # Infrastructure
    REDIS_URL: str = "redis://redis:6379"
    DATABASE_URL: str = "postgresql://supersmartmatch:password@postgres:5432/supersmartmatch"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080"
    ]
    
    # Timeouts (en secondes)
    HTTP_TIMEOUT: int = 30
    CIRCUIT_BREAKER_TIMEOUT: int = 60
    CIRCUIT_BREAKER_THRESHOLD: int = 5
    
    # Monitoring
    METRICS_ENABLED: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Health checks
    HEALTH_CHECK_INTERVAL: int = 30
    SERVICE_TIMEOUT: int = 5
    
    @validator('ALLOWED_ORIGINS', pre=True)
    def parse_cors_origins(cls, value):
        """Parse les origines CORS depuis une string ou liste"""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(',')]
        return value
    
    @validator('DEBUG', pre=True)
    def parse_debug(cls, value):
        """Parse le mode debug"""
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return value
    
    @validator('ENVIRONMENT')
    def validate_environment(cls, value):
        """Valide l'environnement"""
        valid_envs = ['development', 'staging', 'production']
        if value not in valid_envs:
            raise ValueError(f'Environment doit être un de: {valid_envs}')
        return value
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


class DevelopmentSettings(Settings):
    """Configuration pour l'environnement de développement"""
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    RATE_LIMIT_PER_MINUTE: int = 1000  # Plus permissif en dev


class ProductionSettings(Settings):
    """Configuration pour l'environnement de production"""
    DEBUG: bool = False
    LOG_LEVEL: str = "WARNING"
    RATE_LIMIT_PER_MINUTE: int = 50  # Plus strict en production
    JWT_EXPIRE_HOURS: int = 2  # Tokens plus courts en prod


class TestingSettings(Settings):
    """Configuration pour les tests"""
    DEBUG: bool = True
    ENVIRONMENT: str = "testing"
    CV_PARSER_URL: str = "http://localhost:5051"
    JOB_PARSER_URL: str = "http://localhost:5053"
    MATCHING_SERVICE_URL: str = "http://localhost:5060"
    REDIS_URL: str = "redis://localhost:6379"
    JWT_EXPIRE_HOURS: int = 1
    RATE_LIMIT_PER_MINUTE: int = 10000  # Pas de limite en test


@lru_cache()
def get_settings() -> Settings:
    """
    Factory pour obtenir les paramètres selon l'environnement
    Cache les paramètres pour éviter les re-lectures
    """
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    if environment == "production":
        return ProductionSettings()
    elif environment == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()


# Instance globale des paramètres
settings = get_settings()
