"""
🔧 SuperSmartMatch V2 - Configuration Models

Modèles Pydantic pour validation des requêtes/réponses
et configuration centralisée du service unifié
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator

class AlgorithmType(str, Enum):
    """Types d'algorithmes disponibles"""
    NEXTEN = "nexten"
    SMART_MATCH = "smart"
    ENHANCED = "enhanced" 
    SEMANTIC = "semantic"
    BASIC = "basic"
    AUTO = "auto"

class Priority(str, Enum):
    """Niveaux de priorité"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

# ===== MODÈLES DE REQUÊTE =====

class CandidateProfile(BaseModel):
    """Profil candidat avec validation"""
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = Field(None, ge=16, le=100)
    location: Optional[str] = None
    localisation: Optional[str] = None  # Compatibilité format français
    
    # Compétences (formats multiples supportés)
    technical_skills: Optional[List[Union[str, Dict[str, Any]]]] = []
    competences: Optional[List[Union[str, Dict[str, Any]]]] = []
    skills: Optional[List[Union[str, Dict[str, Any]]]] = []
    
    # Expériences
    experiences: Optional[List[Dict[str, Any]]] = []
    experience_years: Optional[float] = Field(None, ge=0, le=50)
    
    # Formation
    education: Optional[List[Dict[str, Any]]] = []
    certifications: Optional[List[str]] = []
    
    # Préférences
    salary_expectation: Optional[Dict[str, Any]] = None
    remote_preference: Optional[str] = None
    mobility: Optional[bool] = None

    @validator('technical_skills', 'competences', 'skills', pre=True)
    def validate_skills(cls, v):
        """Normalise les compétences en liste"""
        if v is None:
            return []
        if isinstance(v, str):
            return [v]
        return v

class CandidateQuestionnaire(BaseModel):
    """Questionnaire candidat pour Nexten Matcher"""
    work_style: Optional[str] = None
    culture_preferences: Optional[str] = None
    remote_preference: Optional[str] = None
    team_size_preference: Optional[str] = None
    management_style: Optional[str] = None
    career_goals: Optional[str] = None
    values: Optional[List[str]] = []
    motivations: Optional[List[str]] = []
    
    # Scores psychométriques
    personality_scores: Optional[Dict[str, float]] = {}
    cognitive_abilities: Optional[Dict[str, float]] = {}
    
    # Validation des scores
    @validator('personality_scores', 'cognitive_abilities')
    def validate_scores(cls, v):
        """Valide que les scores sont entre 0 et 1"""
        if v:
            for key, score in v.items():
                if not (0 <= score <= 1):
                    raise ValueError(f"Score {key} doit être entre 0 et 1")
        return v

class JobOffer(BaseModel):
    """Offre d'emploi avec validation"""
    id: Union[str, int]
    title: str = Field(..., min_length=1)
    company: Optional[str] = None
    
    # Localisation  
    location: Optional[str] = None
    localisation: Optional[str] = None  # Compatibilité
    remote_policy: Optional[str] = None
    
    # Compétences requises
    required_skills: Optional[List[Union[str, Dict[str, Any]]]] = []
    competences: Optional[List[Union[str, Dict[str, Any]]]] = []
    skills: Optional[List[Union[str, Dict[str, Any]]]] = []
    
    # Conditions
    salary_range: Optional[Dict[str, Any]] = None
    contract_type: Optional[str] = None
    experience_required: Optional[str] = None
    
    # Description
    description: Optional[str] = None
    requirements: Optional[List[str]] = []
    benefits: Optional[List[str]] = []

    @validator('required_skills', 'competences', 'skills', pre=True)
    def validate_skills(cls, v):
        """Normalise les compétences"""
        if v is None:
            return []
        if isinstance(v, str):
            return [v]
        return v

class CompanyQuestionnaire(BaseModel):
    """Questionnaire entreprise pour matching culturel"""
    culture: Optional[str] = None
    values: Optional[List[str]] = []
    team_size: Optional[str] = None
    work_methodology: Optional[str] = None
    management_style: Optional[str] = None
    growth_stage: Optional[str] = None
    industry: Optional[str] = None
    
    # Environnement de travail
    office_environment: Optional[str] = None
    flexibility: Optional[Dict[str, Any]] = {}
    benefits: Optional[List[str]] = []

class MatchingConfig(BaseModel):
    """Configuration de matching"""
    algorithm: AlgorithmType = AlgorithmType.AUTO
    weights: Optional[Dict[str, float]] = None
    thresholds: Optional[Dict[str, float]] = None
    max_results: int = Field(default=10, ge=1, le=100)
    
    # Options avancées
    enable_cache: bool = True
    cache_ttl: int = Field(default=300, ge=60, le=3600)
    timeout_ms: int = Field(default=5000, ge=1000, le=30000)
    
    # Filtres
    location_radius_km: Optional[float] = Field(None, ge=0, le=1000)
    salary_tolerance: Optional[float] = Field(None, ge=0, le=1.0)

class V2MatchRequest(BaseModel):
    """Requête de matching V2 complète"""
    candidate: CandidateProfile
    offers: List[JobOffer] = Field(..., min_items=1, max_items=1000)
    
    # Questionnaires optionnels pour Nexten
    candidate_questionnaire: Optional[CandidateQuestionnaire] = None
    company_questionnaires: Optional[List[CompanyQuestionnaire]] = None
    
    # Configuration
    algorithm: AlgorithmType = AlgorithmType.AUTO
    config: Optional[MatchingConfig] = None
    
    # Métadonnées
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ab_test_group: Optional[str] = None

# ===== MODÈLES DE RÉPONSE =====

class MatchResult(BaseModel):
    """Résultat de matching pour une offre"""
    offer_id: str
    overall_score: float = Field(..., ge=0, le=1)
    confidence: float = Field(..., ge=0, le=1)
    
    # Scores détaillés
    skill_match_score: float = Field(default=0.0, ge=0, le=1)
    experience_match_score: float = Field(default=0.0, ge=0, le=1)
    location_match_score: float = Field(default=0.0, ge=0, le=1)
    culture_match_score: float = Field(default=0.0, ge=0, le=1)
    salary_match_score: float = Field(default=0.0, ge=0, le=1)
    
    # Explications
    insights: List[str] = []
    explanation: str = ""
    
    # Métadonnées  
    algorithm_used: Optional[str] = None
    processing_time_ms: Optional[float] = None
    
    class Config:
        """Configuration Pydantic"""
        schema_extra = {
            "example": {
                "offer_id": "job_123",
                "overall_score": 0.87,
                "confidence": 0.92,
                "skill_match_score": 0.95,
                "experience_match_score": 0.82,
                "location_match_score": 1.0,
                "culture_match_score": 0.75,
                "insights": [
                    "Excellent match technique Python/ML",
                    "Localisation parfaite avec préférence hybride",
                    "Culture innovation alignée"
                ],
                "explanation": "Match optimal basé sur expertise technique et fit culturel"
            }
        }

class ContextAnalysis(BaseModel):
    """Analyse du contexte pour sélection d'algorithme"""
    has_complete_questionnaire: bool = False
    questionnaire_completeness: float = Field(default=0.0, ge=0, le=1)
    has_location_constraints: bool = False
    mobility_mentioned: bool = False
    is_senior_profile: bool = False
    experience_years: float = 0.0
    complex_skills_detected: bool = False
    skills_complexity_score: float = Field(default=0.0, ge=0, le=1)
    offers_count: int = 0
    candidate_fields: int = 0

class AlgorithmMetrics(BaseModel):
    """Métriques de performance d'un algorithme"""
    name: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time_ms: float = 0.0
    success_rate: float = Field(default=0.0, ge=0, le=1)
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    circuit_breaker_open: bool = False

class ServiceStatus(BaseModel):
    """Status d'un service externe"""
    name: str
    url: str
    status: str  # "healthy", "degraded", "down"
    last_check: datetime
    response_time_ms: Optional[float] = None
    error_message: Optional[str] = None

class V2MatchResponse(BaseModel):
    """Réponse de matching V2 complète"""
    success: bool
    matches: List[MatchResult]
    
    # Métadonnées d'exécution
    algorithm_used: str
    execution_time_ms: float
    selection_reason: str
    
    # Analyse et contexte
    context_analysis: Optional[ContextAnalysis] = None
    
    # Métadonnées avancées
    metadata: Dict[str, Any] = {}
    
    # Informations de cache et fallback
    cache_hit: bool = False
    fallback_used: bool = False
    circuit_breaker_states: Optional[Dict[str, str]] = None
    
    class Config:
        """Configuration Pydantic"""
        schema_extra = {
            "example": {
                "success": True,
                "matches": [
                    {
                        "offer_id": "job_123",
                        "overall_score": 0.92,
                        "confidence": 0.88,
                        "skill_match_score": 0.95,
                        "insights": ["Excellent technical match"],
                        "explanation": "High match due to Python/ML expertise"
                    }
                ],
                "algorithm_used": "nexten",
                "execution_time_ms": 75.5,
                "selection_reason": "Complete questionnaire data available",
                "cache_hit": False,
                "fallback_used": False
            }
        }

# ===== MODÈLES DE MONITORING =====

class HealthStatus(BaseModel):
    """Status de santé du service"""
    status: str  # "healthy", "degraded", "down"
    version: str = "2.0.0"
    timestamp: datetime
    uptime_seconds: int
    
    # Statistiques globales
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time_ms: float = 0.0
    
    # Status des services externes
    external_services: List[ServiceStatus] = []
    
    # Métriques des algorithmes
    algorithm_metrics: Dict[str, AlgorithmMetrics] = {}
    
    # Circuit breakers
    circuit_breakers: Dict[str, Dict[str, Any]] = {}

class SystemMetrics(BaseModel):
    """Métriques système détaillées"""
    service_name: str = "SuperSmartMatch V2"
    version: str = "2.0.0"
    timestamp: datetime
    
    # Performance
    requests_per_minute: float = 0.0
    avg_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    error_rate: float = Field(default=0.0, ge=0, le=1)
    
    # Utilisation des algorithmes
    algorithm_usage: Dict[str, int] = {}
    algorithm_performance: Dict[str, AlgorithmMetrics] = {}
    
    # Cache
    cache_hit_rate: float = Field(default=0.0, ge=0, le=1)
    cache_size: int = 0
    
    # Services externes
    external_service_health: Dict[str, ServiceStatus] = {}

# ===== MODÈLES DE CONFIGURATION =====

class AlgorithmConfig(BaseModel):
    """Configuration d'un algorithme"""
    enabled: bool = True
    timeout_ms: int = Field(default=5000, ge=100, le=30000)
    priority: Priority = Priority.MEDIUM
    fallback_enabled: bool = True
    cache_ttl: int = Field(default=300, ge=60, le=3600)
    
    # Circuit breaker
    circuit_breaker_threshold: int = Field(default=5, ge=1, le=100)
    circuit_breaker_timeout: int = Field(default=60, ge=10, le=600)

class ServiceConfiguration(BaseModel):
    """Configuration complète du service"""
    version: str = "2.0.0"
    environment: str = "production"
    port: int = Field(default=5070, ge=1000, le=65535)
    
    # Services externes
    nexten_url: str = "http://localhost:5052"
    supersmartmatch_v1_url: str = "http://localhost:5062"
    redis_url: str = "redis://localhost:6379"
    
    # Configuration des algorithmes
    algorithms: Dict[str, AlgorithmConfig] = {
        "nexten": AlgorithmConfig(priority=Priority.HIGH),
        "smart": AlgorithmConfig(priority=Priority.MEDIUM),
        "enhanced": AlgorithmConfig(priority=Priority.MEDIUM),
        "semantic": AlgorithmConfig(priority=Priority.MEDIUM),
        "basic": AlgorithmConfig(priority=Priority.LOW, fallback_enabled=False)
    }
    
    # Performance
    max_response_time_ms: int = Field(default=100, ge=50, le=10000)
    cache_enabled: bool = True
    default_cache_ttl: int = Field(default=300, ge=60, le=3600)
    
    # Feature flags
    enable_v2: bool = True
    enable_ab_testing: bool = True
    v2_traffic_percentage: int = Field(default=100, ge=0, le=100)
    
    # Monitoring
    enable_metrics: bool = True
    metrics_retention_days: int = Field(default=30, ge=1, le=365)

# ===== MODÈLES D'ERREUR =====

class ErrorResponse(BaseModel):
    """Réponse d'erreur standardisée"""
    success: bool = False
    error_code: str
    error_message: str
    timestamp: datetime
    request_id: Optional[str] = None
    
    # Détails techniques (development uniquement)
    details: Optional[Dict[str, Any]] = None
    stack_trace: Optional[str] = None

class ValidationError(BaseModel):
    """Erreur de validation"""
    field: str
    message: str
    invalid_value: Any = None

class ValidationErrorResponse(ErrorResponse):
    """Réponse d'erreur de validation"""
    error_code: str = "VALIDATION_ERROR"
    validation_errors: List[ValidationError] = []

# ===== EXPORT =====

__all__ = [
    # Enums
    'AlgorithmType', 'Priority',
    
    # Modèles de requête
    'CandidateProfile', 'CandidateQuestionnaire', 'JobOffer', 
    'CompanyQuestionnaire', 'MatchingConfig', 'V2MatchRequest',
    
    # Modèles de réponse  
    'MatchResult', 'ContextAnalysis', 'V2MatchResponse',
    
    # Monitoring
    'AlgorithmMetrics', 'ServiceStatus', 'HealthStatus', 'SystemMetrics',
    
    # Configuration
    'AlgorithmConfig', 'ServiceConfiguration',
    
    # Erreurs
    'ErrorResponse', 'ValidationError', 'ValidationErrorResponse'
]
