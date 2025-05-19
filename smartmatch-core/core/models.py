"""
Core Data Models for SmartMatcher
---------------------------------
Définit les classes de données principales utilisées dans le système de matching.
Suit les principes SOLID avec des responsabilités clairement définies.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum


class EducationLevel(Enum):
    """Niveaux d'éducation standardisés"""
    NONE = "none"
    HIGH_SCHOOL = "high_school"
    ASSOCIATE = "associate" 
    BACHELOR = "bachelor"
    MASTER = "master"
    PHD = "phd"


class ContractType(Enum):
    """Types de contrat standardisés"""
    CDI = "cdi"
    CDD = "cdd"
    FREELANCE = "freelance"
    INTERNSHIP = "internship"
    APPRENTICESHIP = "apprenticeship"


class WorkMode(Enum):
    """Modes de travail standardisés"""
    ON_SITE = "on_site"
    HYBRID = "hybrid"
    FULL_REMOTE = "full_remote"


class MatchCategory(Enum):
    """Catégories de qualité de match"""
    EXCELLENT = "excellent"
    GOOD = "good" 
    MODERATE = "moderate"
    WEAK = "weak"
    INSUFFICIENT = "insufficient"


@dataclass
class Location:
    """Représente une localisation géographique"""
    address: str
    city: Optional[str] = None
    country: Optional[str] = None
    coordinates: Optional[tuple] = None  # (latitude, longitude)
    
    def __str__(self) -> str:
        return self.address
    
    def to_coordinates_string(self) -> Optional[str]:
        """Convertit en format 'lat,lng' pour les APIs"""
        if self.coordinates:
            return f"{self.coordinates[0]},{self.coordinates[1]}"
        return None


@dataclass
class SalaryRange:
    """Représente une fourchette salariale"""
    min_amount: int
    max_amount: int
    currency: str = "EUR"
    period: str = "yearly"  # yearly, monthly, daily, hourly
    
    def contains(self, amount: int) -> bool:
        """Vérifie si un montant est dans la fourchette"""
        return self.min_amount <= amount <= self.max_amount
    
    def overlaps_with(self, other: 'SalaryRange') -> bool:
        """Vérifie si deux fourchettes se chevauchent"""
        return not (self.max_amount < other.min_amount or self.min_amount > other.max_amount)


@dataclass
class Candidate:
    """Modèle représentant un candidat"""
    id: str
    name: str
    skills: List[str] = field(default_factory=list)
    experience_years: int = 0
    education_level: EducationLevel = EducationLevel.NONE
    location: Optional[Location] = None
    preferences: Dict[str, Any] = field(default_factory=dict)
    
    # Informations supplémentaires du CV
    job_title: str = ""
    summary: str = ""
    experience_description: str = ""
    
    # Préférences de travail
    preferred_work_mode: Optional[WorkMode] = None
    preferred_contract_type: Optional[ContractType] = None
    salary_expectation: Optional[SalaryRange] = None
    max_commute_time: int = 60  # minutes
    preferred_company_size: Optional[str] = None
    preferred_industries: List[str] = field(default_factory=list)
    
    # Disponibilité
    available_from: Optional[datetime] = None
    
    def get_normalized_skills(self) -> List[str]:
        """Retourne les compétences normalisées (lowercase, stripped)"""
        return [skill.lower().strip() for skill in self.skills if skill.strip()]
    
    def has_skill(self, skill: str) -> bool:
        """Vérifie si le candidat possède une compétence"""
        normalized_skills = self.get_normalized_skills()
        return skill.lower().strip() in normalized_skills
    
    def get_location_string(self) -> str:
        """Retourne la localisation sous forme de string"""
        return str(self.location) if self.location else ""


@dataclass
class Job:
    """Modèle représentant une offre d'emploi"""
    id: str
    title: str
    company_name: str
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    description: str = ""
    
    # Exigences
    min_experience_years: int = 0
    max_experience_years: Optional[int] = None
    required_education: EducationLevel = EducationLevel.NONE
    
    # Localisation et mode de travail
    location: Optional[Location] = None
    work_mode: WorkMode = WorkMode.ON_SITE
    
    # Contrat et compensation
    contract_type: ContractType = ContractType.CDI
    salary_range: Optional[SalaryRange] = None
    
    # Informations entreprise
    company_size: Optional[str] = None
    industry: str = ""
    company_values: List[str] = field(default_factory=list)
    
    # Dates
    start_date: Optional[datetime] = None
    application_deadline: Optional[datetime] = None
    
    def get_all_skills(self) -> List[str]:
        """Retourne toutes les compétences (requises + préférées)"""
        return self.required_skills + self.preferred_skills
    
    def get_normalized_required_skills(self) -> List[str]:
        """Retourne les compétences requises normalisées"""
        return [skill.lower().strip() for skill in self.required_skills if skill.strip()]
    
    def get_normalized_preferred_skills(self) -> List[str]:
        """Retourne les compétences préférées normalisées"""
        return [skill.lower().strip() for skill in self.preferred_skills if skill.strip()]
    
    def requires_skill(self, skill: str) -> bool:
        """Vérifie si une compétence est requise"""
        return skill.lower().strip() in self.get_normalized_required_skills()
    
    def prefers_skill(self, skill: str) -> bool:
        """Vérifie si une compétence est préférée"""
        return skill.lower().strip() in self.get_normalized_preferred_skills()
    
    def get_location_string(self) -> str:
        """Retourne la localisation sous forme de string"""
        return str(self.location) if self.location else ""


@dataclass
class MatchInsight:
    """Représente un insight sur un match"""
    type: str  # 'strength', 'weakness', 'recommendation', 'mismatch'
    category: str  # 'skills', 'location', 'experience', etc.
    message: str
    score: Optional[float] = None
    priority: int = 1  # 1=low, 2=medium, 3=high
    
    def __str__(self) -> str:
        return f"[{self.category.upper()}] {self.message}"


@dataclass
class MatchResult:
    """Résultat complet d'un calcul de matching"""
    candidate_id: str
    job_id: str
    overall_score: float
    category_scores: Dict[str, float] = field(default_factory=dict)
    insights: List[MatchInsight] = field(default_factory=list)
    
    # Métadonnées
    computed_at: datetime = field(default_factory=datetime.now)
    computation_time_ms: Optional[float] = None
    algorithm_version: str = "2.0.0"
    
    def get_category(self) -> MatchCategory:
        """Détermine la catégorie du match basée sur le score global"""
        if self.overall_score >= 0.85:
            return MatchCategory.EXCELLENT
        elif self.overall_score >= 0.70:
            return MatchCategory.GOOD
        elif self.overall_score >= 0.50:
            return MatchCategory.MODERATE
        elif self.overall_score >= 0.30:
            return MatchCategory.WEAK
        else:
            return MatchCategory.INSUFFICIENT
    
    def get_strengths(self) -> List[MatchInsight]:
        """Retourne les forces du match"""
        return [insight for insight in self.insights if insight.type == 'strength']
    
    def get_weaknesses(self) -> List[MatchInsight]:
        """Retourne les faiblesses du match"""
        return [insight for insight in self.insights if insight.type == 'weakness']
    
    def get_recommendations(self) -> List[MatchInsight]:
        """Retourne les recommandations"""
        return [insight for insight in self.insights if insight.type == 'recommendation']
    
    def add_insight(self, insight: MatchInsight) -> None:
        """Ajoute un insight au résultat"""
        self.insights.append(insight)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le résultat en dictionnaire"""
        return {
            'candidate_id': self.candidate_id,
            'job_id': self.job_id,
            'overall_score': self.overall_score,
            'category': self.get_category().value,
            'category_scores': self.category_scores,
            'insights': [
                {
                    'type': insight.type,
                    'category': insight.category,
                    'message': insight.message,
                    'score': insight.score,
                    'priority': insight.priority
                }
                for insight in self.insights
            ],
            'computed_at': self.computed_at.isoformat(),
            'computation_time_ms': self.computation_time_ms,
            'algorithm_version': self.algorithm_version
        }


@dataclass
class BatchMatchRequest:
    """Requête pour un matching en lot"""
    candidates: List[Candidate]
    jobs: List[Job]
    filters: Dict[str, Any] = field(default_factory=dict)
    limit_per_candidate: int = 10
    limit_per_job: int = 50
    min_score_threshold: float = 0.3
    
    def validate(self) -> bool:
        """Valide la requête"""
        if not self.candidates or not self.jobs:
            return False
        if self.min_score_threshold < 0 or self.min_score_threshold > 1:
            return False
        return True


@dataclass
class BatchMatchResult:
    """Résultat d'un matching en lot"""
    matches: List[MatchResult]
    total_processed: int
    processing_time_ms: float
    candidates_matched: int
    jobs_matched: int
    
    # Statistiques
    avg_score: float = 0.0
    min_score: float = 0.0
    max_score: float = 0.0
    
    def __post_init__(self):
        """Calcule les statistiques après initialisation"""
        if self.matches:
            scores = [match.overall_score for match in self.matches]
            self.avg_score = sum(scores) / len(scores)
            self.min_score = min(scores)
            self.max_score = max(scores)
