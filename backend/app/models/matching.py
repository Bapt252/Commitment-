from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime


class ScoreDetail(BaseModel):
    """Détail d'un score de matching pour une catégorie spécifique"""
    category: str
    score: float
    explanation: Optional[str] = None


class MatchingRequestBase(BaseModel):
    """Modèle de base pour une requête de matching"""
    min_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Score minimum pour filtrer les résultats")
    limit: int = Field(default=10, ge=1, le=100, description="Nombre maximum de résultats à retourner")


class JobCandidateMatchingRequest(MatchingRequestBase):
    """Requête pour matcher des candidats à une fiche de poste"""
    job_post_id: int
    candidate_ids: Optional[List[int]] = None


class CandidateJobMatchingRequest(MatchingRequestBase):
    """Requête pour matcher des fiches de poste à un candidat"""
    candidate_id: int
    job_post_ids: Optional[List[int]] = None


class MatchingResult(BaseModel):
    """Résultat d'un matching entre une fiche de poste et un candidat"""
    job_post_id: int
    candidate_id: int
    overall_score: float = Field(ge=0.0, le=1.0)
    score_details: List[ScoreDetail]
    strengths: List[str]
    gaps: List[str]
    recommendations: List[str]
    created_at: datetime


class MatchingResponse(MatchingResult):
    """Réponse complète avec informations enrichies sur le matching"""
    id: Optional[int] = None
    job_title: Optional[str] = None
    job_company: Optional[str] = None
    job_location: Optional[str] = None
    candidate_name: Optional[str] = None
    candidate_profile: Optional[Dict[str, Any]] = None
    match_details: Dict[str, Any] = Field(default_factory=dict)


class MatchingBatchResult(BaseModel):
    """Résultat global d'une opération de matching par lot"""
    total_matches: int
    matches: List[MatchingResponse]
    average_score: float
    processing_time_ms: int


class MatchingFilter(BaseModel):
    """Filtres pour la recherche de matchings"""
    min_score: float = 0.0
    max_score: float = 1.0
    job_post_id: Optional[int] = None
    candidate_id: Optional[int] = None
    skills: Optional[List[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = 1
    per_page: int = 10


class MatchingInDB(MatchingResult):
    """Modèle pour un matching stocké en base de données"""
    id: int

    class Config:
        orm_mode = True
