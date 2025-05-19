"""
Preferences Value Objects

Représente les préférences des candidats.
"""

from dataclasses import dataclass
from datetime import datetime, date
from typing import List, Optional, Set
from enum import Enum


class JobType(Enum):
    """
    Types de postes disponibles.
    """
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    FREELANCE = "freelance"
    INTERNSHIP = "internship"
    TEMPORARY = "temporary"


class WorkMode(Enum):
    """
    Modes de travail.
    """
    ON_SITE = "on_site"
    REMOTE = "remote"
    HYBRID = "hybrid"


@dataclass(frozen=True)
class CandidatePreferences:
    """
    Représente les préférences d'un candidat.
    """
    
    job_types: Set[JobType]
    work_mode: WorkMode
    remote_work_acceptable: bool = True
    max_commute_time_minutes: Optional[int] = None
    preferred_industries: Set[str] = None
    availability_date: Optional[date] = None
    expected_salary_min: Optional[int] = None
    expected_salary_max: Optional[int] = None
    company_size_preferences: Optional[str] = None  # 'startup', 'sme', 'large_corp'
    
    def __post_init__(self):
        if self.job_types is None:
            object.__setattr__(self, 'job_types', set())
        
        if self.preferred_industries is None:
            object.__setattr__(self, 'preferred_industries', set())
        
        if self.expected_salary_min is not None and self.expected_salary_min < 0:
            raise ValueError("Expected minimum salary cannot be negative")
        
        if (self.expected_salary_min is not None and 
            self.expected_salary_max is not None and 
            self.expected_salary_max < self.expected_salary_min):
            raise ValueError("Expected maximum salary cannot be less than minimum")
    
    @classmethod
    def flexible(cls) -> 'CandidatePreferences':
        """
        Crée des préférences flexibles (accepte la plupart des options).
        
        Returns:
            Préférences flexibles
        """
        return cls(
            job_types={JobType.FULL_TIME, JobType.CONTRACT, JobType.FREELANCE},
            work_mode=WorkMode.HYBRID,
            remote_work_acceptable=True,
            max_commute_time_minutes=90
        )
    
    @classmethod
    def remote_only(cls) -> 'CandidatePreferences':
        """
        Crée des préférences pour le travail à distance uniquement.
        
        Returns:
            Préférences pour télétravail
        """
        return cls(
            job_types={JobType.FULL_TIME, JobType.CONTRACT, JobType.FREELANCE},
            work_mode=WorkMode.REMOTE,
            remote_work_acceptable=True,
            max_commute_time_minutes=None
        )
    
    def accepts_job_type(self, job_type: JobType) -> bool:
        """
        Vérifie si le candidat accepte un type de poste.
        
        Args:
            job_type: Type de poste à vérifier
            
        Returns:
            True si le type de poste est accepté
        """
        return job_type in self.job_types
    
    def remote_work_compatible(self, job_offers_remote: bool) -> bool:
        """
        Vérifie la compatibilité avec les options de télétravail.
        
        Args:
            job_offers_remote: True si le poste offre le télétravail
            
        Returns:
            Score de compatibilité (True si compatible)
        """
        if self.work_mode == WorkMode.REMOTE:
            return job_offers_remote
        elif self.work_mode == WorkMode.ON_SITE:
            return True  # Peut travailler sur site même si remote est offert
        else:  # HYBRID
            return True  # Flexible
    
    def is_available_at(self, start_date: str) -> bool:
        """
        Vérifie si le candidat est disponible à une date donnée.
        
        Args:
            start_date: Date de début au format ISO (YYYY-MM-DD)
            
        Returns:
            True si le candidat est disponible
        """
        if self.availability_date is None:
            return True  # Disponible immédiatement
        
        try:
            job_start = datetime.strptime(start_date, "%Y-%m-%d").date()
            return job_start >= self.availability_date
        except ValueError:
            # Format de date invalide, on considère comme compatible
            return True
    
    def salary_compatibility_score(self, offered_salary_min: int, offered_salary_max: int) -> float:
        """
        Calcule un score de compatibilité salariale.
        
        Args:
            offered_salary_min: Salaire minimum offert
            offered_salary_max: Salaire maximum offert
            
        Returns:
            Score entre 0 et 1
        """
        if self.expected_salary_min is None:
            return 1.0  # Pas d'attente spécifique
        
        # Vérifier si les fourchettes se chevauchent
        candidate_max = self.expected_salary_max or float('inf')
        
        # Chevauchement complet
        if (self.expected_salary_min <= offered_salary_max and 
            candidate_max >= offered_salary_min):
            return 1.0
        
        # Candidat demande plus que ce qui est offert
        if self.expected_salary_min > offered_salary_max:
            gap = self.expected_salary_min - offered_salary_max
            gap_ratio = gap / offered_salary_max if offered_salary_max > 0 else 1
            return max(0.0, 1.0 - gap_ratio * 2)  # Pénalité pour écart
        
        # Candidat demande moins (pas vraiment un problème)
        return 0.8
    
    def industry_match_score(self, job_industry: str) -> float:
        """
        Calcule un score de correspondance sectorielle.
        
        Args:
            job_industry: Secteur de l'offre d'emploi
            
        Returns:
            Score entre 0 et 1
        """
        if not self.preferred_industries:
            return 0.8  # Pas de préférence spécifique
        
        # Correspondance exacte
        if job_industry in self.preferred_industries:
            return 1.0
        
        # Correspondance partielle (recherche de mots-clés)
        job_lower = job_industry.lower()
        for preferred in self.preferred_industries:
            if preferred.lower() in job_lower or job_lower in preferred.lower():
                return 0.7
        
        return 0.3  # Pas de correspondance
    
    def commute_acceptable(self, commute_time_minutes: int) -> bool:
        """
        Vérifie si un temps de trajet est acceptable.
        
        Args:
            commute_time_minutes: Temps de trajet en minutes
            
        Returns:
            True si le temps de trajet est acceptable
        """
        if self.work_mode == WorkMode.REMOTE:
            return True  # Pas de trajet nécessaire
        
        if self.max_commute_time_minutes is None:
            return True  # Pas de limite spécifiée
        
        return commute_time_minutes <= self.max_commute_time_minutes
    
    @property
    def expected_salary_range(self) -> Optional[range]:
        """
        Retourne la fourchette salariale attendue.
        
        Returns:
            Range de salaire ou None si non spécifié
        """
        if self.expected_salary_min is None:
            return None
        
        max_salary = self.expected_salary_max or (self.expected_salary_min * 2)
        return range(self.expected_salary_min, max_salary + 1)
    
    def __str__(self) -> str:
        job_types_str = ", ".join(jt.value for jt in self.job_types)
        return f"Preferences(job_types=[{job_types_str}], work_mode={self.work_mode.value})"
    
    def __repr__(self) -> str:
        return self.__str__()
