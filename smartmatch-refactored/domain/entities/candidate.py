"""
Candidate Entity

Représente un candidat avec ses compétences, expérience et préférences.
"""

from dataclasses import dataclass
from typing import List, Optional

from ..value_objects import (
    SkillSet, 
    Location, 
    ExperienceLevel, 
    EducationLevel,
    CandidatePreferences
)


@dataclass(frozen=True)
class Candidate:
    """
    Entité représentant un candidat à l'emploi.
    
    Cette entité est immutable et contient toutes les informations
    nécessaires pour effectuer le matching avec des offres d'emploi.
    """
    
    id: str
    name: str
    skills: SkillSet
    location: Location
    experience: ExperienceLevel
    education: EducationLevel
    preferences: CandidatePreferences
    
    def has_skill(self, skill_name: str) -> bool:
        """
        Vérifie si le candidat possède une compétence spécifique.
        
        Args:
            skill_name: Nom de la compétence à vérifier
            
        Returns:
            True si le candidat possède la compétence, False sinon
        """
        return self.skills.contains(skill_name)
    
    def matches_remote_preference(self, job_offers_remote: bool) -> bool:
        """
        Vérifie si l'offre d'emploi correspond aux préférences de télétravail.
        
        Args:
            job_offers_remote: True si l'offre propose le télétravail
            
        Returns:
            True si les préférences correspondent, False sinon
        """
        return self.preferences.remote_work_compatible(job_offers_remote)
    
    def is_available_at(self, start_date: str) -> bool:
        """
        Vérifie si le candidat est disponible à une date donnée.
        
        Args:
            start_date: Date de début au format ISO (YYYY-MM-DD)
            
        Returns:
            True si le candidat est disponible, False sinon
        """
        return self.preferences.is_available_at(start_date)
    
    def get_expected_salary_range(self) -> Optional[range]:
        """
        Retourne la fourchette salariale attendue par le candidat.
        
        Returns:
            Range de salaire attendu ou None si non spécifié
        """
        return self.preferences.expected_salary_range
    
    def __str__(self) -> str:
        return f"Candidate(id='{self.id}', name='{self.name}')"
    
    def __repr__(self) -> str:
        return self.__str__()
