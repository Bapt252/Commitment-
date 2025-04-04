from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime


class Skill(BaseModel):
    """Modèle pour une compétence technique"""
    name: str
    level: Optional[int] = None
    description: Optional[str] = None


class JobPostBase(BaseModel):
    """Modèle de base pour une fiche de poste"""
    title: str
    description: str
    company: Optional[str] = None
    location: Optional[str] = None
    contract_type: Optional[str] = None
    salary_range: Optional[str] = None
    skills: List[Skill] = []


class JobPostCreate(JobPostBase):
    """Modèle pour la création d'une fiche de poste"""
    pass


class JobPostUpdate(BaseModel):
    """Modèle pour la mise à jour d'une fiche de poste"""
    title: Optional[str] = None
    description: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    contract_type: Optional[str] = None
    salary_range: Optional[str] = None
    skills: Optional[List[Skill]] = None


class JobPostInDB(JobPostBase):
    """Modèle pour une fiche de poste stockée en base de données"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class JobPostResponse(JobPostInDB):
    """Modèle de réponse pour une fiche de poste"""
    pass


class JobPostParseResponse(JobPostBase):
    """Modèle de réponse pour l'analyse d'une fiche de poste"""
    confidence_scores: Dict[str, float] = Field(default_factory=dict, description="Scores de confiance pour chaque champ extrait")
    raw_extraction: Dict[str, Any] = Field(default_factory=dict, description="Données brutes d'extraction pour le debugging")


class JobPostSearchParams(BaseModel):
    """Paramètres de recherche pour les fiches de poste"""
    query: Optional[str] = None
    skills: Optional[List[str]] = None
    location: Optional[str] = None
    contract_type: Optional[str] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    page: int = 1
    per_page: int = 10
