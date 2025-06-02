"""
Modèles pour la gestion des algorithmes et circuit breakers

Définit les structures pour :
- Types et statuts d'algorithmes
- États des circuit breakers
- Sélection intelligente
- Métriques par algorithme
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


class AlgorithmType(str, Enum):
    """Types d'algorithmes de matching disponibles"""
    AUTO = "auto"  # Sélection automatique
    NEXTEN = "nexten"  # Nexten Matcher (40K lignes ML)
    SMART_MATCH = "smart-match"  # Géolocalisation
    ENHANCED = "enhanced"  # Profils seniors
    SEMANTIC = "semantic"  # NLP complexe
    HYBRID = "hybrid"  # Combinaison
    BASIC = "basic"  # Fallback simple


class CircuitBreakerState(str, Enum):
    """États possibles d'un circuit breaker"""
    CLOSED = "closed"  # Fonctionnel
    OPEN = "open"  # En panne, utilise fallback
    HALF_OPEN = "half_open"  # Test de récupération


class AlgorithmSelection(BaseModel):
    """Résultat de la sélection d'algorithme"""
    
    # Algorithme sélectionné
    selected_algorithm: AlgorithmType
    
    # Scores et raisons
    selection_score: float = Field(..., ge=0, le=100)
    selection_reasons: List[str] = Field(default_factory=list)
    
    # Analyse des données d'entrée
    input_analysis: Dict[str, Any] = Field(default_factory=dict)
    
    # Algorithmes alternatifs
    alternative_algorithms: List[AlgorithmType] = Field(default_factory=list)
    fallback_order: List[AlgorithmType] = Field(default_factory=list)
    
    # Métadonnées
    timestamp: datetime = Field(default_factory=datetime.now)
    forced: bool = Field(False, description="Algorithme forcé par l'utilisateur")
    
    # Performance prédite
    predicted_performance: Optional[Dict[str, float]] = None


class AlgorithmStatus(BaseModel):
    """Statut d'un algorithme spécifique"""
    
    # Identification
    algorithm: AlgorithmType
    name: str
    version: Optional[str] = None
    
    # État opérationnel
    is_available: bool = True
    circuit_breaker_state: CircuitBreakerState = CircuitBreakerState.CLOSED
    
    # Métriques de performance
    success_rate: float = Field(0.0, ge=0, le=1)
    average_response_time_ms: float = 0.0
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    
    # Circuit breaker
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    next_retry_time: Optional[datetime] = None
    
    # Configuration
    timeout_ms: int = 30000
    max_retries: int = 3
    failure_threshold: int = 5
    
    # Santé du service externe
    external_service_url: Optional[str] = None
    last_health_check: Optional[datetime] = None
    health_check_success: bool = True
    
    # Métadonnées
    last_used: Optional[datetime] = None
    priority: int = Field(5, ge=1, le=10, description="Priorité (1=max, 10=min)")
    tags: List[str] = Field(default_factory=list)


class InputDataAnalysis(BaseModel):
    """Analyse des données d'entrée pour sélection d'algorithme"""
    
    # Scores par critère
    questionnaire_completeness_score: float = Field(0.0, ge=0, le=100)
    location_data_quality_score: float = Field(0.0, ge=0, le=100)
    skills_complexity_score: float = Field(0.0, ge=0, le=100)
    experience_level_score: float = Field(0.0, ge=0, le=100)
    
    # Indicateurs booléens
    has_complete_questionnaire: bool = False
    has_location_data: bool = False
    has_complex_skills: bool = False
    is_senior_profile: bool = False
    
    # Compteurs
    num_skills: int = 0
    num_jobs: int = 0
    num_locations: int = 0
    
    # Score global
    global_data_richness_score: float = Field(0.0, ge=0, le=100)
    
    # Recommandations
    recommended_algorithms: List[AlgorithmType] = Field(default_factory=list)
    data_quality_warnings: List[str] = Field(default_factory=list)


class AlgorithmPerformanceMetrics(BaseModel):
    """Métriques de performance pour un algorithme"""
    
    algorithm: AlgorithmType
    
    # Métriques temporelles
    period_start: datetime
    period_end: datetime
    
    # Statistiques de base
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    
    # Performance
    min_response_time_ms: Optional[float] = None
    max_response_time_ms: Optional[float] = None
    avg_response_time_ms: float = 0.0
    p95_response_time_ms: Optional[float] = None
    
    # Qualité
    avg_match_score: float = 0.0
    avg_results_count: float = 0.0
    
    # Utilisation
    selection_count: int = 0
    fallback_usage_count: int = 0
    
    # Tendances
    performance_trend: Optional[str] = None  # "improving", "degrading", "stable"
    reliability_score: float = Field(0.0, ge=0, le=1)


class CircuitBreakerMetrics(BaseModel):
    """Métriques spécifiques aux circuit breakers"""
    
    algorithm: AlgorithmType
    
    # État actuel
    current_state: CircuitBreakerState
    state_duration_seconds: int = 0
    
    # Compteurs
    state_transitions: Dict[str, int] = Field(default_factory=dict)
    total_open_duration_seconds: int = 0
    
    # Échecs
    consecutive_failures: int = 0
    total_failures_today: int = 0
    
    # Récupération
    recovery_attempts: int = 0
    successful_recoveries: int = 0
    
    # Configuration active
    failure_threshold: int = 5
    recovery_timeout_seconds: int = 60
    
    # Derniers événements
    last_failure_reason: Optional[str] = None
    last_state_change: Optional[datetime] = None


class AlgorithmSelectionConfig(BaseModel):
    """Configuration pour la sélection d'algorithme"""
    
    # Seuils de sélection
    nexten_min_score: int = 80
    senior_experience_threshold: int = 10
    complex_skills_threshold: int = 5
    
    # Pondérations
    questionnaire_weight: float = 0.4
    location_weight: float = 0.2
    skills_weight: float = 0.2
    experience_weight: float = 0.2
    
    # Ordre de priorité
    priority_order: List[AlgorithmType] = Field(default_factory=lambda: [
        AlgorithmType.NEXTEN,
        AlgorithmType.ENHANCED,
        AlgorithmType.SMART_MATCH,
        AlgorithmType.SEMANTIC,
        AlgorithmType.BASIC
    ])
    
    # Fallback
    enable_fallback: bool = True
    max_fallback_attempts: int = 3
    
    # Cache de sélection
    cache_selection_results: bool = True
    cache_ttl_seconds: int = 1800  # 30 minutes
