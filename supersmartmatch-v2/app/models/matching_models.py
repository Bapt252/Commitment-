"""
Modèles Pydantic pour les requêtes et réponses de matching

Définit les structures de données pour :
- Requêtes V1 et V2
- Données CV et jobs
- Réponses et résultats
- Monitoring et santé
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from enum import Enum


class AlgorithmType(str, Enum):
    """Types d'algorithmes disponibles"""
    AUTO = "auto"
    NEXTEN = "nexten"
    SMART_MATCH = "smart-match"
    ENHANCED = "enhanced"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"
    BASIC = "basic"


class CVData(BaseModel):
    """Données du CV candidat"""
    
    # Informations de base
    nom: Optional[str] = None
    prenom: Optional[str] = None
    age: Optional[int] = None
    localisation: Optional[str] = None
    
    # Compétences et expérience
    competences: List[str] = Field(default_factory=list)
    experience: Optional[int] = Field(None, description="Années d'expérience")
    niveau_etudes: Optional[str] = None
    certifications: List[str] = Field(default_factory=list)
    
    # Préférences
    salaire_souhaite: Optional[int] = None
    type_contrat_souhaite: Optional[str] = None
    mobilite_km: Optional[int] = Field(None, description="Rayon de mobilité en km")
    teletravail_accepte: Optional[bool] = None
    
    # Questionnaire et données enrichies
    questionnaire_complete: bool = Field(False, description="Questionnaire complet rempli")
    profil_comportemental: Optional[Dict[str, Any]] = None
    preferences_detaillees: Optional[Dict[str, Any]] = None
    
    # Métadonnées
    derniere_mise_a_jour: Optional[datetime] = None
    score_completude: Optional[float] = Field(None, ge=0, le=100)
    
    @validator('experience')
    def validate_experience(cls, v):
        if v is not None and (v < 0 or v > 50):
            raise ValueError('L\'expérience doit être entre 0 et 50 ans')
        return v
    
    @validator('age')
    def validate_age(cls, v):
        if v is not None and (v < 16 or v > 70):
            raise ValueError('L\'âge doit être entre 16 et 70 ans')
        return v


class JobData(BaseModel):
    """Données d'un poste/job"""
    
    # Identifiant unique
    id: str = Field(..., description="Identifiant unique du job")
    
    # Informations de base
    titre: Optional[str] = None
    entreprise: Optional[str] = None
    localisation: Optional[str] = None
    description: Optional[str] = None
    
    # Exigences techniques
    competences: List[str] = Field(default_factory=list)
    experience_requise: Optional[int] = Field(None, description="Années d'expérience requises")
    niveau_etudes_requis: Optional[str] = None
    certifications_requises: List[str] = Field(default_factory=list)
    
    # Conditions
    salaire_min: Optional[int] = None
    salaire_max: Optional[int] = None
    type_contrat: Optional[str] = None
    teletravail_possible: Optional[bool] = None
    
    # Métadonnées
    secteur: Optional[str] = None
    taille_entreprise: Optional[str] = None
    date_publication: Optional[datetime] = None
    urgence: Optional[str] = Field(None, description="Niveau d'urgence du recrutement")
    
    # Score et priorité
    score_attractivite: Optional[float] = Field(None, ge=0, le=100)
    priorite: Optional[str] = Field("normale", description="Priorité du job")


class MatchingOptions(BaseModel):
    """Options pour personnaliser le matching"""
    
    # Algorithme
    force_algorithm: Optional[AlgorithmType] = Field(
        None, 
        description="Forcer l'utilisation d'un algorithme spécifique"
    )
    
    # Limites
    max_results: int = Field(10, ge=1, le=100, description="Nombre maximum de résultats")
    min_score: float = Field(0.0, ge=0, le=100, description="Score minimum pour inclusion")
    
    # Comportement
    enable_fallback: bool = Field(True, description="Activer le fallback en cas d'échec")
    enable_caching: bool = Field(True, description="Activer la mise en cache")
    
    # Géolocalisation
    max_distance_km: Optional[int] = Field(
        None, 
        description="Distance maximum en km (si géolocalisation)"
    )
    include_travel_time: bool = Field(
        False, 
        description="Inclure le temps de trajet dans les résultats"
    )
    
    # Personnalisation
    user_id: Optional[str] = Field(None, description="ID utilisateur pour personnalisation")
    context: Optional[Dict[str, Any]] = Field(
        None, 
        description="Contexte additionnel pour l'algorithme"
    )


class MatchResult(BaseModel):
    """Résultat d'un match entre CV et job"""
    
    # Identifiants
    job_id: str
    
    # Scores
    score_global: float = Field(..., ge=0, le=100, description="Score global de matching")
    score_competences: Optional[float] = Field(None, ge=0, le=100)
    score_experience: Optional[float] = Field(None, ge=0, le=100)
    score_localisation: Optional[float] = Field(None, ge=0, le=100)
    score_salaire: Optional[float] = Field(None, ge=0, le=100)
    
    # Détails du matching
    competences_matchees: List[str] = Field(default_factory=list)
    competences_manquantes: List[str] = Field(default_factory=list)
    
    # Géolocalisation (si disponible)
    distance_km: Optional[float] = None
    temps_trajet_minutes: Optional[int] = None
    moyen_transport: Optional[str] = None
    
    # Explications
    raisons_match: List[str] = Field(default_factory=list)
    recommandations: List[str] = Field(default_factory=list)
    
    # Métadonnées
    algorithme_utilise: str
    confiance: Optional[float] = Field(None, ge=0, le=1, description="Niveau de confiance")
    timestamp: datetime = Field(default_factory=datetime.now)


class MatchingRequestV1(BaseModel):
    """Requête de matching format V1 (compatibilité)"""
    
    cv_data: CVData
    job_data: List[JobData]  # V1 utilise 'job_data'
    algorithm: Optional[str] = "auto"
    options: Optional[Dict[str, Any]] = None


class MatchingRequestV2(BaseModel):
    """Requête de matching format V2 (nouveau)"""
    
    cv_data: CVData
    jobs: List[JobData]  # V2 utilise 'jobs'
    options: Optional[MatchingOptions] = None
    
    @validator('jobs')
    def validate_jobs_limit(cls, v):
        if len(v) > 100:  # Limite configurable
            raise ValueError('Maximum 100 jobs par requête')
        return v


class MatchingResponse(BaseModel):
    """Réponse de matching unifiée"""
    
    # Résultats
    matches: List[MatchResult]
    
    # Métadonnées de la requête
    algorithme_utilise: str
    temps_traitement_ms: Optional[int] = None
    
    # Statistiques
    total_jobs_analyses: int
    jobs_matches: int
    score_moyen: Optional[float] = None
    
    # Informations système
    version: str = "2.0.0"
    timestamp: datetime = Field(default_factory=datetime.now)
    fallback_utilise: bool = False
    
    # Cache et performance
    depuis_cache: bool = False
    services_externes_utilises: List[str] = Field(default_factory=list)
    
    # Recommandations globales
    recommandations_generales: List[str] = Field(default_factory=list)
    ameliorations_possibles: List[str] = Field(default_factory=list)


class HealthResponse(BaseModel):
    """Réponse de vérification de santé"""
    
    status: str  # "healthy", "unhealthy", "degraded"
    version: str
    timestamp: float
    
    # Services externes
    external_services: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # Détails en cas de problème
    error: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)
    
    # Informations système
    uptime_seconds: Optional[float] = None
    memory_usage: Optional[Dict[str, Any]] = None


class MetricsResponse(BaseModel):
    """Réponse avec métriques de performance"""
    
    # Métriques générales
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time_ms: float = 0.0
    
    # Utilisation des algorithmes
    algorithm_usage: Dict[str, int] = Field(default_factory=dict)
    
    # Circuit breakers
    circuit_breaker_states: Dict[str, str] = Field(default_factory=dict)
    
    # Cache
    cache_hit_rate: float = 0.0
    cache_size: int = 0
    
    # Services externes
    external_services_health: Dict[str, bool] = Field(default_factory=dict)
    external_services_response_times: Dict[str, float] = Field(default_factory=dict)
    
    # Période de collecte
    collection_period_hours: int = 1
    last_reset: datetime = Field(default_factory=datetime.now)
    
    # Tendances
    trends: Optional[Dict[str, Any]] = None
