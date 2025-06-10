"""
Configuration centralisée pour SuperSmartMatch V2

Gestion des variables d'environnement et des paramètres
de configuration pour tous les composants du service.
"""

import os
from functools import lru_cache
from typing import List, Optional
from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """Configuration principale de l'application"""
    
    # === CONFIGURATION PRINCIPALE ===
    port: int = 5070
    debug: bool = False
    log_level: str = "INFO"
    secret_key: str = "supersmartmatch-v2-secret-key-change-in-production"
    
    # === SERVICES EXTERNES ===
    nexten_matcher_url: str = "http://matching-api:5052"
    supersmartmatch_v1_url: str = "http://supersmartmatch-service:5062"
    
    # === REDIS CONFIGURATION ===
    redis_url: str = "redis://redis:6379/0"
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    cache_ttl: int = 3600  # 1 heure
    
    # === CIRCUIT BREAKERS ===
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_recovery_timeout: int = 60
    circuit_breaker_expected_exception: str = "RequestException"
    
    # === ALGORITHMES ET SÉLECTION ===
    default_algorithm: str = "auto"
    enable_intelligent_selection: bool = True
    enable_fallback: bool = True
    
    # Seuils pour sélection d'algorithme
    nexten_matcher_threshold: int = 80  # Score pour utiliser Nexten
    senior_experience_threshold: int = 10  # Années pour Enhanced
    complex_skills_threshold: int = 5  # Nombre de compétences pour Semantic
    
    # === PERFORMANCE ET LIMITES ===
    max_jobs_per_request: int = 100
    max_concurrent_requests: int = 50
    request_timeout: int = 30  # secondes
    max_retries: int = 3
    
    # === MONITORING ===
    monitoring_enabled: bool = True
    metrics_retention_hours: int = 24
    enable_detailed_logging: bool = False
    
    # === SÉCURITÉ ET CORS ===
    cors_origins: List[str] = ["*"]
    enable_rate_limiting: bool = True
    rate_limit_per_minute: int = 100
    rate_limit_per_hour: int = 1000
    
    # === OPTIMISATIONS ===
    enable_caching: bool = True
    enable_request_batching: bool = True
    batch_size: int = 10
    
    # === FALLBACK CONFIGURATION ===
    fallback_algorithm_order: List[str] = [
        "nexten", "enhanced", "smart-match", "semantic", "basic"
    ]
    
    @validator('log_level')
    def validate_log_level(cls, v):
        """Valider le niveau de log"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'log_level doit être un de: {valid_levels}')
        return v.upper()
    
    @validator('fallback_algorithm_order')
    def validate_fallback_order(cls, v):
        """Valider l'ordre de fallback"""
        valid_algorithms = ['nexten', 'enhanced', 'smart-match', 'semantic', 'basic']
        for algo in v:
            if algo not in valid_algorithms:
                raise ValueError(f'Algorithme inconnu: {algo}')
        return v
    
    @validator('cors_origins', pre=True)
    def validate_cors_origins(cls, v):
        """Parser les origines CORS depuis string ou liste"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class AlgorithmConfig:
    """Configuration spécifique aux algorithmes"""
    
    # === NEXTEN MATCHER ===
    # CORRECTION: Nexten utilise /match et non /api/match
    NEXTEN_ENDPOINT = "/match"
    NEXTEN_TIMEOUT = 30
    NEXTEN_RETRY_ATTEMPTS = 3
    
    # === SUPERSMARTMATCH V1 ===
    V1_ENDPOINT = "/api/v1/match"
    V1_TIMEOUT = 25
    V1_RETRY_ATTEMPTS = 3
    
    # Mapping des algorithmes V1
    V1_ALGORITHMS = {
        "smart-match": "smart-match",
        "enhanced": "enhanced",
        "semantic": "semantic", 
        "hybrid": "hybrid",
        "basic": "basic"
    }
    
    # === SEUILS DE SÉLECTION ===
    QUESTIONNAIRE_COMPLETE_WEIGHT = 40
    LOCATION_DATA_WEIGHT = 20
    COMPLEX_SKILLS_WEIGHT = 20
    SENIOR_PROFILE_WEIGHT = 20
    
    # Seuils de score pour sélection
    NEXTEN_MIN_SCORE = 80
    ENHANCED_MIN_EXPERIENCE = 10
    SEMANTIC_MIN_SKILLS = 5


class MonitoringConfig:
    """Configuration du monitoring"""
    
    # Métriques à collecter
    METRICS_TO_COLLECT = [
        "request_count",
        "algorithm_usage",
        "response_time",
        "success_rate",
        "circuit_breaker_state",
        "cache_hit_rate"
    ]
    
    # Rétention des métriques
    METRICS_RETENTION = {
        "detailed": 3600,  # 1 heure
        "aggregated": 86400,  # 24 heures
        "summary": 604800  # 1 semaine
    }
    
    # Alertes
    ALERT_THRESHOLDS = {
        "error_rate": 0.05,  # 5%
        "response_time_p95": 5.0,  # 5 secondes
        "circuit_breaker_open": True
    }


class CacheConfig:
    """Configuration du cache Redis"""
    
    # Clés de cache
    CACHE_KEYS = {
        "matching_result": "match:result:{hash}",
        "algorithm_selection": "algo:select:{hash}",
        "service_health": "health:{service}",
        "metrics": "metrics:{type}:{timestamp}"
    }
    
    # TTL par type de cache
    CACHE_TTL = {
        "matching_result": 3600,  # 1 heure
        "algorithm_selection": 1800,  # 30 minutes
        "service_health": 300,  # 5 minutes
        "metrics": 86400  # 24 heures
    }
    
    # Configuration Redis
    REDIS_CONFIG = {
        "socket_keepalive": True,
        "socket_keepalive_options": {},
        "connection_pool_kwargs": {
            "max_connections": 50,
            "retry_on_timeout": True
        }
    }


@lru_cache()
def get_settings() -> Settings:
    """Factory pour obtenir la configuration (avec cache)"""
    return Settings()


def get_algorithm_config() -> AlgorithmConfig:
    """Obtenir la configuration des algorithmes"""
    return AlgorithmConfig()


def get_monitoring_config() -> MonitoringConfig:
    """Obtenir la configuration du monitoring"""
    return MonitoringConfig()


def get_cache_config() -> CacheConfig:
    """Obtenir la configuration du cache"""
    return CacheConfig()


# Variables d'environnement pour le développement
if __name__ == "__main__":
    settings = get_settings()
    print("=== Configuration SuperSmartMatch V2 ===")
    print(f"Port: {settings.port}")
    print(f"Debug: {settings.debug}")
    print(f"Log Level: {settings.log_level}")
    print(f"Nexten Matcher: {settings.nexten_matcher_url}")
    print(f"SuperSmartMatch V1: {settings.supersmartmatch_v1_url}")
    print(f"Redis: {settings.redis_url}")
    print(f"Circuit Breaker Threshold: {settings.circuit_breaker_failure_threshold}")
    print(f"Cache TTL: {settings.cache_ttl}")
    print(f"Fallback Order: {settings.fallback_algorithm_order}")
