"""
Configuration centralisée pour SuperSmartMatch V2
"""

import os
from typing import Optional, List
from pydantic import BaseSettings, Field
from functools import lru_cache

class SuperSmartMatchV2Config(BaseSettings):
    """Configuration du service SuperSmartMatch V2"""
    
    # Configuration de base
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    port: int = Field(default=5070, env="PORT")
    
    # Configuration des services externes
    nexten_matcher_url: str = Field(default="http://localhost:5052", env="NEXTEN_MATCHER_URL")
    supersmartmatch_v1_url: str = Field(default="http://localhost:5062", env="SUPERSMARTMATCH_V1_URL")
    
    # Features flags
    enable_nexten: bool = Field(default=True, env="ENABLE_NEXTEN")
    enable_smart_selection: bool = Field(default=True, env="ENABLE_SMART_SELECTION")
    enable_v1_compatibility: bool = Field(default=True, env="ENABLE_V1_COMPATIBILITY")
    enable_circuit_breaker: bool = Field(default=True, env="ENABLE_CIRCUIT_BREAKER")
    enable_caching: bool = Field(default=True, env="ENABLE_CACHING")
    
    # Configuration performance
    max_response_time_ms: int = Field(default=100, env="MAX_RESPONSE_TIME_MS")
    default_timeout_ms: int = Field(default=30000, env="DEFAULT_TIMEOUT_MS")
    nexten_timeout_ms: int = Field(default=80000, env="NEXTEN_TIMEOUT_MS")
    v1_timeout_ms: int = Field(default=20000, env="V1_TIMEOUT_MS")
    
    # Configuration circuit breaker
    circuit_breaker_failure_threshold: int = Field(default=5, env="CB_FAILURE_THRESHOLD")
    circuit_breaker_recovery_timeout: int = Field(default=60, env="CB_RECOVERY_TIMEOUT")
    circuit_breaker_expected_exception: str = Field(default="Exception", env="CB_EXPECTED_EXCEPTION")
    
    # Configuration cache Redis
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")
    
    # Configuration rate limiting
    rate_limit_per_minute: int = Field(default=100, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_per_hour: int = Field(default=1000, env="RATE_LIMIT_PER_HOUR")
    
    # Configuration des règles de sélection d'algorithme
    questionnaire_completeness_threshold: float = Field(default=0.8, env="QUESTIONNAIRE_COMPLETENESS_THRESHOLD")
    senior_experience_years: int = Field(default=7, env="SENIOR_EXPERIENCE_YEARS")
    skills_complexity_threshold: float = Field(default=0.6, env="SKILLS_COMPLEXITY_THRESHOLD")
    
    # Configuration de logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    # Configuration monitoring
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_retention_days: int = Field(default=30, env="METRICS_RETENTION_DAYS")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Instance globale de configuration avec cache
@lru_cache()
def get_config() -> SuperSmartMatchV2Config:
    """Obtenir la configuration (avec cache)"""
    return SuperSmartMatchV2Config()

# Configuration pour les tests
class TestConfig(SuperSmartMatchV2Config):
    """Configuration spécialisée pour les tests"""
    debug: bool = True
    enable_circuit_breaker: bool = False
    nexten_matcher_url: str = "http://mock-nexten:5052"
    supersmartmatch_v1_url: str = "http://mock-v1:5062"
    redis_url: str = "redis://localhost:6379/15"  # DB différente pour tests
    
    class Config:
        env_prefix = "TEST_"