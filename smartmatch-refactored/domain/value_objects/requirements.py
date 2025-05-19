"""
Requirements Value Objects

Représente les exigences des offres d'emploi.
"""

from dataclasses import dataclass
from typing import List, Optional, Set
from datetime import date
from .preferences import JobType, WorkMode


@dataclass(frozen=True)
class JobRequirements:
    """
    Représente les exigences d'une offre d'emploi.
    """
    
    start_date: Optional[date] = None
    job_type: Optional[JobType] = None
    work_mode: Optional[WorkMode] = None
    language_requirements: Set[str] = None
    certifications_required: Set[str] = None
    background_check_required: bool = False
    travel_required: bool = False
    max_travel_percentage: Optional[int] = None
    
    def __post_init__(self):
        if self.language_requirements is None:
            object.__setattr__(self, 'language_requirements', set())
            
        if self.certifications_required is None:
            object.__setattr__(self, 'certifications_required', set())
        
        if self.max_travel_percentage is not None:
            if self.max_travel_percentage < 0 or self.max_travel_percentage > 100:
                raise ValueError("Travel percentage must be between 0 and 100")
    
    @classmethod
    def basic(cls, job_type: JobType = JobType.FULL_TIME) -> 'JobRequirements':
        """
        Crée des exigences de base pour un poste.
        
        Args:
            job_type: Type de poste
            
        Returns:
            Exigences de base
        """
        return cls(
            job_type=job_type,
            work_mode=WorkMode.HYBRID,
            travel_required=False
        )
    
    @classmethod
    def remote_friendly(cls) -> 'JobRequirements':
        """
        Crée des exigences adaptées au télétravail.
        
        Returns:
            Exigences pour télétravail
        """
        return cls(
            job_type=JobType.FULL_TIME,
            work_mode=WorkMode.REMOTE,
            travel_required=False,
            background_check_required=False
        )
    
    def requires_language(self, language: str) -> bool:
        """
        Vérifie si une langue spécifique est requise.
        
        Args:
            language: Langue à vérifier
            
        Returns:
            True si la langue est requise
        """
        return language.lower() in {lang.lower() for lang in self.language_requirements}
    
    def requires_certification(self, certification: str) -> bool:
        """
        Vérifie si une certification spécifique est requise.
        
        Args:
            certification: Certification à vérifier
            
        Returns:
            True si la certification est requise
        """
        return certification.lower() in {cert.lower() for cert in self.certifications_required}
    
    def start_date_compatibility(self, candidate_availability: Optional[date]) -> float:
        """
        Calcule la compatibilité avec la date de disponibilité du candidat.
        
        Args:
            candidate_availability: Date de disponibilité du candidat
            
        Returns:
            Score entre 0 et 1
        """
        if self.start_date is None:
            return 1.0  # Pas de date de début spécifique
        
        if candidate_availability is None:
            return 1.0  # Candidat disponible immédiatement
        
        if candidate_availability <= self.start_date:
            return 1.0  # Candidat disponible avant la date souhaitée
        
        # Calculer le retard en jours
        delay_days = (candidate_availability - self.start_date).days
        
        # Pénalité progressive pour retard
        if delay_days <= 30:  # Moins d'un mois de retard
            return 0.8
        elif delay_days <= 90:  # Moins de 3 mois
            return 0.5
        else:  # Plus de 3 mois
            return 0.2
    
    def work_mode_compatibility(self, candidate_work_mode: WorkMode) -> float:
        """
        Calcule la compatibilité avec le mode de travail préféré du candidat.
        
        Args:
            candidate_work_mode: Mode de travail préféré du candidat
            
        Returns:
            Score entre 0 et 1
        """
        if self.work_mode is None:
            return 0.8  # Pas de préférence spécifiée
        
        # Correspondance exacte
        if self.work_mode == candidate_work_mode:
            return 1.0
        
        # Compatibilités partielles
        compatibility_matrix = {
            (WorkMode.HYBRID, WorkMode.REMOTE): 0.8,
            (WorkMode.HYBRID, WorkMode.ON_SITE): 0.8,
            (WorkMode.REMOTE, WorkMode.HYBRID): 0.7,
            (WorkMode.ON_SITE, WorkMode.HYBRID): 0.7,
            (WorkMode.REMOTE, WorkMode.ON_SITE): 0.3,
            (WorkMode.ON_SITE, WorkMode.REMOTE): 0.3
        }
        
        return compatibility_matrix.get((self.work_mode, candidate_work_mode), 0.5)
    
    def travel_compatibility(self, candidate_accepts_travel: bool) -> float:
        """
        Calcule la compatibilité avec les déplacements.
        
        Args:
            candidate_accepts_travel: True si le candidat accepte les déplacements
            
        Returns:
            Score entre 0 et 1
        """
        if not self.travel_required:
            return 1.0  # Pas de déplacement requis
        
        if candidate_accepts_travel:
            return 1.0  # Le candidat accepte les déplacements
        
        # Pénalité en fonction du pourcentage de déplacement
        if self.max_travel_percentage is None:
            return 0.3  # Déplacement requis mais pourcentage non spécifié
        
        if self.max_travel_percentage <= 10:
            return 0.7  # Déplacement occasionnel
        elif self.max_travel_percentage <= 25:
            return 0.5  # Déplacement modéré
        else:
            return 0.2  # Déplacement fréquent
    
    def __str__(self) -> str:
        parts = []
        if self.job_type:
            parts.append(f"type: {self.job_type.value}")
        if self.work_mode:
            parts.append(f"mode: {self.work_mode.value}")
        if self.travel_required:
            travel_str = f"travel: {self.max_travel_percentage}%" if self.max_travel_percentage else "travel: required"
            parts.append(travel_str)
        
        return f"JobRequirements({', '.join(parts)})"
    
    def __repr__(self) -> str:
        return self.__str__()
