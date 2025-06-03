"""
Modèles Pydantic pour SuperSmartMatch V2

Définit les structures de données pour les requêtes et réponses
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, validator
from enum import Enum
import time

# Énumérations
class AlgorithmType(str, Enum):
    """Types d'algorithmes disponibles"""
    AUTO = "auto"
    NEXTEN = "nexten_matcher"
    ENHANCED = "enhanced_match"
    SMART = "smart_match"
    SEMANTIC = "semantic_match"
    BASIC = "basic_match"

class MatchConfidence(str, Enum):
    """Niveaux de confiance du matching"""
    VERY_HIGH = "very_high"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    VERY_LOW = "very_low"

# Modèles de base
class Skill(BaseModel):
    """Compétence technique ou soft skill"""
    name: str = Field(..., description="Nom de la compétence")
    level: Optional[str] = Field(None, description="Niveau de maîtrise")
    years: Optional[int] = Field(None, description="Années d'expérience")
    category: Optional[str] = Field(None, description="Catégorie de compétence")

class Experience(BaseModel):
    """Expérience professionnelle"""
    title: str = Field(..., description="Titre du poste")
    company: str = Field(..., description="Nom de l'entreprise")
    duration_months: Optional[int] = Field(None, description="Durée en mois")
    skills: List[str] = Field(default=[], description="Compétences utilisées")
    description: Optional[str] = Field(None, description="Description du poste")

class Location(BaseModel):
    """Localisation géographique"""
    city: Optional[str] = Field(None, description="Ville")
    country: Optional[str] = Field(None, description="Pays")
    postal_code: Optional[str] = Field(None, description="Code postal")
    latitude: Optional[float] = Field(None, description="Latitude")
    longitude: Optional[float] = Field(None, description="Longitude")

class Questionnaire(BaseModel):
    """Questionnaire candidat/entreprise"""
    work_style: Optional[str] = Field(None, description="Style de travail préféré")
    culture_preferences: Optional[str] = Field(None, description="Préférences culturelles")
    remote_preference: Optional[str] = Field(None, description="Préférence télétravail")
    career_goals: Optional[List[str]] = Field(None, description="Objectifs de carrière")
    values: Optional[List[str]] = Field(None, description="Valeurs importantes")
    
# Modèles pour les candidats et offres
class Candidate(BaseModel):
    """Modèle candidat"""
    id: Optional[str] = Field(None, description="Identifiant unique")
    name: str = Field(..., description="Nom du candidat")
    email: Optional[str] = Field(None, description="Email")
    technical_skills: List[Union[str, Skill]] = Field(default=[], description="Compétences techniques")
    soft_skills: List[str] = Field(default=[], description="Compétences comportementales")
    experiences: List[Experience] = Field(default=[], description="Expériences professionnelles")
    location: Optional[Location] = Field(None, description="Localisation")
    salary_expectation: Optional[int] = Field(None, description="Prétentions salariales")
    availability: Optional[str] = Field(None, description="Disponibilité")
    
    @validator('technical_skills', pre=True)
    def normalize_skills(cls, v):
        """Normalise les compétences en objets Skill"""
        if not v:
            return []
        
        normalized = []
        for skill in v:
            if isinstance(skill, str):
                normalized.append(Skill(name=skill))
            elif isinstance(skill, dict):
                normalized.append(Skill(**skill))
            else:
                normalized.append(skill)
        return normalized

class JobOffer(BaseModel):
    """Modèle offre d'emploi"""
    id: str = Field(..., description="Identifiant unique de l'offre")
    title: str = Field(..., description="Titre du poste")
    company: str = Field(..., description="Nom de l'entreprise")
    description: Optional[str] = Field(None, description="Description du poste")
    required_skills: List[str] = Field(default=[], description="Compétences requises")
    preferred_skills: List[str] = Field(default=[], description="Compétences souhaitées")
    location: Optional[Location] = Field(None, description="Localisation du poste")
    salary_range: Optional[Dict[str, int]] = Field(None, description="Fourchette salariale")
    remote_policy: Optional[str] = Field(None, description="Politique télétravail")
    experience_level: Optional[str] = Field(None, description="Niveau d'expérience requis")
    contract_type: Optional[str] = Field(None, description="Type de contrat")

# Modèles de requête
class MatchRequestV1(BaseModel):
    """Requête de matching V1 (compatibilité)"""
    candidate: Candidate = Field(..., description="Données du candidat")
    offers: List[JobOffer] = Field(..., description="Liste des offres à matcher")
    algorithm: Optional[AlgorithmType] = Field(AlgorithmType.AUTO, description="Algorithme à utiliser")
    limit: Optional[int] = Field(10, description="Nombre maximum de résultats")
    
    # Support du format legacy "jobs" -> "offers"
    jobs: Optional[List[JobOffer]] = Field(None, description="Format legacy - utiliser 'offers'")
    
    @validator('offers', pre=True, always=True)
    def normalize_offers(cls, v, values):
        """Convertit 'jobs' en 'offers' pour compatibilité"""
        if v is None and 'jobs' in values and values['jobs']:
            return values['jobs']
        return v or []

class MatchRequestV2(BaseModel):
    """Requête de matching V2 (enrichie)"""
    candidate: Candidate = Field(..., description="Données du candidat")
    candidate_questionnaire: Optional[Questionnaire] = Field(None, description="Questionnaire candidat")
    offers: List[JobOffer] = Field(..., description="Liste des offres à matcher")
    company_questionnaires: Optional[List[Questionnaire]] = Field(None, description="Questionnaires entreprises")
    algorithm: Optional[AlgorithmType] = Field(AlgorithmType.AUTO, description="Algorithme à utiliser")
    limit: Optional[int] = Field(10, description="Nombre maximum de résultats")
    include_explanations: bool = Field(True, description="Inclure les explications détaillées")
    preferences: Optional[Dict[str, Any]] = Field(None, description="Préférences de matching")

# Modèles de réponse
class MatchResult(BaseModel):
    """Résultat de matching pour une offre"""
    offer_id: str = Field(..., description="ID de l'offre")
    overall_score: float = Field(..., description="Score global de matching")
    confidence: float = Field(..., description="Niveau de confiance")
    skill_match_score: Optional[float] = Field(None, description="Score de matching des compétences")
    experience_match_score: Optional[float] = Field(None, description="Score de matching de l'expérience")
    location_match_score: Optional[float] = Field(None, description="Score de matching géographique")
    culture_match_score: Optional[float] = Field(None, description="Score de matching culturel")
    
    # Détails pour V1 (compatibilité)
    details: Optional[Dict[str, Any]] = Field(None, description="Détails de matching V1")
    
    # Enrichissements V2
    insights: Optional[List[str]] = Field(None, description="Insights sur le matching")
    explanation: Optional[str] = Field(None, description="Explication détaillée")
    strengths: Optional[List[str]] = Field(None, description="Points forts du matching")
    weaknesses: Optional[List[str]] = Field(None, description="Points faibles du matching")
    recommendations: Optional[List[str]] = Field(None, description="Recommandations d'amélioration")

class MatchResponseV1(BaseModel):
    """Réponse de matching V1 (compatibilité)"""
    matches: List[MatchResult] = Field(..., description="Résultats de matching")
    algorithm_used: str = Field(..., description="Algorithme utilisé")
    execution_time_ms: int = Field(..., description="Temps d'exécution en ms")
    total_offers: Optional[int] = Field(None, description="Nombre total d'offres traitées")

class ContextAnalysis(BaseModel):
    """Analyse du contexte pour la sélection d'algorithme"""
    questionnaire_completeness: float = Field(..., description="Complétude du questionnaire")
    skills_complexity: float = Field(..., description="Complexité des compétences")
    experience_level: str = Field(..., description="Niveau d'expérience")
    has_location_constraints: bool = Field(..., description="Contraintes géographiques")
    semantic_analysis_needed: bool = Field(..., description="Analyse sémantique nécessaire")

class PerformanceMetrics(BaseModel):
    """Métriques de performance"""
    cache_hit: bool = Field(..., description="Cache hit")
    fallback_used: bool = Field(..., description="Fallback utilisé")
    algorithm_confidence: float = Field(..., description="Confiance de l'algorithme")
    service_latency_ms: int = Field(..., description="Latence du service")
    circuit_breaker_status: Optional[str] = Field(None, description="Statut du circuit breaker")

class MatchMetadata(BaseModel):
    """Métadonnées de matching"""
    algorithm_used: str = Field(..., description="Algorithme utilisé")
    execution_time_ms: int = Field(..., description="Temps d'exécution")
    selection_reason: str = Field(..., description="Raison de sélection de l'algorithme")
    context_analysis: ContextAnalysis = Field(..., description="Analyse du contexte")
    performance_metrics: PerformanceMetrics = Field(..., description="Métriques de performance")
    fallback_chain: Optional[List[str]] = Field(None, description="Chaîne de fallback utilisée")

class MatchResponseV2(BaseModel):
    """Réponse de matching V2 (enrichie)"""
    success: bool = Field(True, description="Succès de l'opération")
    matches: List[MatchResult] = Field(..., description="Résultats de matching")
    metadata: MatchMetadata = Field(..., description="Métadonnées détaillées")
    total_offers: int = Field(..., description="Nombre total d'offres traitées")
    timestamp: int = Field(default_factory=lambda: int(time.time()), description="Timestamp de la réponse")

# Modèles utilitaires
class HealthResponse(BaseModel):
    """Réponse de santé du service"""
    status: str = Field(..., description="Statut de santé")
    version: str = Field(..., description="Version du service")
    timestamp: int = Field(..., description="Timestamp de vérification")
    services: Dict[str, Any] = Field(..., description="Statut des services externes")
    features: Dict[str, bool] = Field(..., description="Fonctionnalités activées")

class ErrorResponse(BaseModel):
    """Réponse d'erreur standardisée"""
    error: bool = Field(True, description="Indicateur d'erreur")
    message: str = Field(..., description="Message d'erreur")
    status_code: int = Field(..., description="Code de statut HTTP")
    timestamp: int = Field(default_factory=lambda: int(time.time()), description="Timestamp de l'erreur")
    details: Optional[Dict[str, Any]] = Field(None, description="Détails supplémentaires")