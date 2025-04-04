"""
Schémas de données pour le système de matching.
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field


class CandidateProfile(BaseModel):
    """Profil de candidat au format JSON."""
    id: Optional[str] = None
    name: Optional[str] = None
    job_title: Optional[str] = None
    competences: Optional[List[str]] = None
    experience: Optional[List[Dict[str, Any]]] = None
    experience_years: Optional[float] = None
    education: Optional[Any] = None
    education_level: Optional[str] = None
    education_field: Optional[str] = None
    values: Optional[Any] = None
    about_me: Optional[str] = None
    work_preferences: Optional[Dict[str, Any]] = None
    preferred_location: Optional[str] = None
    preferred_work_mode: Optional[str] = None
    expected_salary: Optional[Dict[str, Any]] = None
    preferred_company_size: Optional[str] = None
    preferred_industries: Optional[List[str]] = None
    
    # Permettre des champs supplémentaires
    class Config:
        extra = "allow"


class JobProfile(BaseModel):
    """Profil d'offre d'emploi au format JSON."""
    id: Optional[str] = None
    job_title: Optional[str] = None
    title: Optional[str] = None
    company_name: Optional[str] = None
    company: Optional[str] = None
    description: Optional[str] = None
    job_description: Optional[str] = None
    required_skills: Optional[List[str]] = None
    required_experience_years: Optional[float] = None
    required_education_level: Optional[str] = None
    preferred_education_field: Optional[str] = None
    company_values: Optional[Any] = None
    location: Optional[str] = None
    work_mode: Optional[str] = None
    salary_range: Optional[Dict[str, Any]] = None
    contract_type: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    
    # Permettre des champs supplémentaires
    class Config:
        extra = "allow"


class MatchingRequest(BaseModel):
    """Requête pour un matching candidat-offre."""
    candidates: Optional[List[Dict[str, Any]]] = None
    jobs: Optional[List[Dict[str, Any]]] = None
    candidate_profile: Optional[Dict[str, Any]] = None
    job_profile: Optional[Dict[str, Any]] = None
    limit: Optional[int] = 10


class ExplanationFactor(BaseModel):
    """Facteur d'explication avec son importance."""
    factor: str
    importance: float
    description: str


class CandidateExplanation(BaseModel):
    """Explication du matching pour un candidat."""
    strengths: List[str]
    areas_to_improve: List[str]
    top_factors: List[Dict[str, Any]]


class JobExplanation(BaseModel):
    """Explication du matching pour une offre d'emploi."""
    matching_points: List[str]
    gaps: List[str]
    top_factors: List[Dict[str, Any]]


class CandidateMatchingResponse(BaseModel):
    """Réponse pour un candidat dans le matching."""
    candidate_id: str
    candidate_name: str
    title: Optional[str] = None
    relevance_score: float
    explanation: CandidateExplanation
    match_categories: Dict[str, float]


class JobMatchingResponse(BaseModel):
    """Réponse pour une offre d'emploi dans le matching."""
    job_id: str
    title: str
    company_name: str
    relevance_score: float
    explanation: JobExplanation
    match_categories: Dict[str, float]


class Highlight(BaseModel):
    """Point fort du candidat."""
    type: str
    title: str
    items: List[str]


class Requirement(BaseModel):
    """Exigence du poste."""
    type: str
    title: str
    items: List[str]


class Suggestion(BaseModel):
    """Suggestion d'amélioration."""
    area: str
    suggestion: str


class DetailedFactor(BaseModel):
    """Facteur détaillé avec valeur et impact."""
    factor: str
    importance: float
    impact: float
    value: float
    description: str


class DetailedMatchingResponse(BaseModel):
    """Explication détaillée du matching."""
    match_score: float
    match_summary: str
    recommendation: str
    category_scores: Dict[str, float]
    positive_factors: List[DetailedFactor]
    negative_factors: List[DetailedFactor]
    candidate_highlights: List[Highlight]
    job_requirements: List[Requirement]
    improvement_suggestions: List[Suggestion]
    feature_importance: Dict[str, float]
