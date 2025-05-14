"""
Modèles de données pour le matching bidirectionnel
-------------------------------------------------
Pydantic models pour le service de matching bidirectionnel.

Auteur: Claude/Anthropic
Date: 14/05/2025
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import List, Dict, Any, Optional, Union
from enum import Enum

class MatchingBidirectionalResponse(BaseModel):
    """Réponse à une requête de matching bidirectionnel"""
    job_id: str = Field(..., description="ID du job dans la file d'attente")
    status: str = Field(..., description="Statut du job (queued, running, completed, failed)")
    message: str = Field(..., description="Message informatif")

class JobMatchingRequest(BaseModel):
    """Requête pour trouver les meilleures offres pour un candidat"""
    candidate_id: int = Field(..., description="ID du candidat")
    limit: int = Field(10, description="Nombre maximal de résultats")
    min_score: float = Field(0.3, description="Score minimum pour inclure un match")
    with_commute_time: bool = Field(True, description="Calculer le temps de trajet")
    webhook_url: Optional[str] = Field(None, description="URL de webhook pour notification")

class CandidateMatchingRequest(BaseModel):
    """Requête pour trouver les meilleurs candidats pour une offre"""
    job_id: int = Field(..., description="ID de l'offre d'emploi")
    limit: int = Field(10, description="Nombre maximal de résultats")
    min_score: float = Field(0.3, description="Score minimum pour inclure un match")
    with_commute_time: bool = Field(True, description="Calculer le temps de trajet")
    webhook_url: Optional[str] = Field(None, description="URL de webhook pour notification")

class MatchCategory(str, Enum):
    """Catégorie de matching"""
    EXCELLENT = "excellent"
    GOOD = "good"
    MODERATE = "moderate"
    WEAK = "weak"
    INSUFFICIENT = "insufficient"

class MatchScores(BaseModel):
    """Scores détaillés d'un matching"""
    total: float = Field(..., description="Score global")
    skills: float = Field(..., description="Score des compétences")
    experience: float = Field(..., description="Score de l'expérience")
    description: float = Field(..., description="Score de la description")
    title: float = Field(..., description="Score du titre")

class QuestionnaireScores(BaseModel):
    """Scores basés sur les questionnaires"""
    total: float = Field(..., description="Score global des questionnaires")
    informations_personnelles: float = Field(..., description="Score des informations personnelles")
    mobilite_preferences: float = Field(..., description="Score de mobilité et préférences")
    motivations_secteurs: float = Field(..., description="Score des motivations et secteurs")
    disponibilite_situation: float = Field(..., description="Score de disponibilité et situation")

class MatchDetails(BaseModel):
    """Détails d'un résultat de matching"""
    cv: MatchScores = Field(..., description="Scores basés sur le CV")
    questionnaire: QuestionnaireScores = Field(..., description="Scores basés sur les questionnaires")

class MatchInsights(BaseModel):
    """Insights générés pour un matching"""
    strengths: List[str] = Field(..., description="Points forts du matching")
    areas_of_improvement: List[str] = Field(..., description="Points à améliorer")
    recommendations: List[str] = Field(..., description="Recommandations")

class BidirectionalMatchingResult(BaseModel):
    """Résultat complet d'un matching bidirectionnel"""
    score: float = Field(..., description="Score global de matching")
    category: MatchCategory = Field(..., description="Catégorie de matching")
    details: MatchDetails = Field(..., description="Détails des scores")
    insights: MatchInsights = Field(..., description="Insights pour ce matching")
    timestamp: str = Field(..., description="Timestamp du calcul")

class CandidateBasicInfo(BaseModel):
    """Informations de base sur un candidat"""
    id: int = Field(..., description="ID du candidat")
    name: str = Field(..., description="Nom du candidat")
    job_title: Optional[str] = Field(None, description="Titre du poste actuel")

class JobBasicInfo(BaseModel):
    """Informations de base sur une offre d'emploi"""
    id: int = Field(..., description="ID de l'offre")
    title: str = Field(..., description="Titre du poste")
    company: str = Field(..., description="Nom de l'entreprise")
    location: Optional[str] = Field(None, description="Localisation")

class JobMatchingResultItem(BaseModel):
    """Résultat de matching pour une offre d'emploi"""
    job: JobBasicInfo = Field(..., description="Informations sur l'offre")
    score: float = Field(..., description="Score de matching")
    category: MatchCategory = Field(..., description="Catégorie de matching")
    details: MatchDetails = Field(..., description="Détails des scores")
    insights: MatchInsights = Field(..., description="Insights pour ce matching")

class CandidateMatchingResultItem(BaseModel):
    """Résultat de matching pour un candidat"""
    candidate: CandidateBasicInfo = Field(..., description="Informations sur le candidat")
    score: float = Field(..., description="Score de matching")
    category: MatchCategory = Field(..., description="Catégorie de matching")
    details: MatchDetails = Field(..., description="Détails des scores")
    insights: MatchInsights = Field(..., description="Insights pour ce matching")

class CommuteTimeInfo(BaseModel):
    """Informations sur le temps de trajet"""
    origin: str = Field(..., description="Adresse d'origine")
    destination: str = Field(..., description="Adresse de destination")
    duration_minutes: float = Field(..., description="Durée du trajet en minutes")
    distance_km: float = Field(..., description="Distance en kilomètres")
    transport_mode: str = Field(..., description="Mode de transport utilisé")

class BidirectionalMultipleMatchingResult(BaseModel):
    """Résultat de matching multiple (jobs pour candidat ou candidats pour job)"""
    count: int = Field(..., description="Nombre total de résultats")
    results: Union[List[JobMatchingResultItem], List[CandidateMatchingResultItem]] = Field(
        ..., description="Liste des résultats de matching"
    )
    timestamp: str = Field(..., description="Timestamp du calcul")
    query_parameters: Dict[str, Any] = Field(
        ..., description="Paramètres de la requête utilisés pour obtenir ces résultats"
    )
