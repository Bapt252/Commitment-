"""
JobOffer Entity

Représente une offre d'emploi avec ses exigences et caractéristiques.
"""

from dataclasses import dataclass
from typing import Optional

from ..value_objects import (
    SkillSet,
    Location, 
    ExperienceRange,
    EducationLevel,
    SalaryRange,
    JobRequirements
)


@dataclass(frozen=True)
class JobOffer:
    """
    Entité représentant une offre d'emploi.
    
    Cette entité est immutable et contient toutes les informations
    nécessaires pour effectuer le matching avec des candidats.
    """
    
    id: str
    title: str
    company: str
    required_skills: SkillSet
    preferred_skills: SkillSet
    location: Location
    experience_range: ExperienceRange
    required_education: EducationLevel
    salary_range: SalaryRange
    offers_remote: bool
    job_type: str  # 'full_time', 'part_time', 'contract', etc.
    industry: str
    requirements: JobRequirements
    
    def meets_experience_requirement(self, candidate_experience: int) -> bool:
        """
        Vérifie si l'expérience du candidat répond aux exigences du poste.
        
        Args:
            candidate_experience: Nombre d'années d'expérience du candidat
            
        Returns:
            True si l'expérience répond aux exigences, False sinon
        """
        return self.experience_range.contains(candidate_experience)
    
    def requires_skill(self, skill_name: str) -> bool:
        """
        Vérifie si une compétence est requise pour ce poste.
        
        Args:
            skill_name: Nom de la compétence à vérifier
            
        Returns:
            True si la compétence est requise, False sinon
        """
        return self.required_skills.contains(skill_name)
    
    def prefers_skill(self, skill_name: str) -> bool:
        """
        Vérifie si une compétence est préférée pour ce poste.
        
        Args:
            skill_name: Nom de la compétence à vérifier
            
        Returns:
            True si la compétence est préférée, False sinon
        """
        return self.preferred_skills.contains(skill_name)
    
    def get_all_desired_skills(self) -> SkillSet:
        """
        Retourne toutes les compétences désirées (requises + préférées).
        
        Returns:
            SkillSet contenant toutes les compétences
        """
        return self.required_skills.union(self.preferred_skills)
    
    def salary_matches(self, expected_salary: int) -> bool:
        """
        Vérifie si le salaire proposé correspond aux attentes.
        
        Args:
            expected_salary: Salaire attendu par le candidat
            
        Returns:
            True si compatible, False sinon
        """
        return self.salary_range.contains(expected_salary)
    
    def __str__(self) -> str:
        return f"JobOffer(id='{self.id}', title='{self.title}', company='{self.company}')"
    
    def __repr__(self) -> str:
        return self.__str__()
