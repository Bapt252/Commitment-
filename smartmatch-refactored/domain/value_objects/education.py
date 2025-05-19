"""
Education Value Object

Représente les niveaux d'éducation.
"""

from enum import Enum
from typing import List


class EducationLevel(Enum):
    """
    Niveaux d'éducation standardisés.
    
    Chaque niveau a une valeur numérique pour faciliter les comparaisons.
    """
    NONE = (0, "No formal education")
    HIGH_SCHOOL = (1, "High School / Secondary Education")
    ASSOCIATE = (2, "Associate Degree / Technical Diploma")
    BACHELOR = (3, "Bachelor's Degree")
    MASTER = (4, "Master's Degree")
    PHD = (5, "Doctorate / PhD")
    
    def __init__(self, level: int, description: str):
        self.level = level
        self.description = description
    
    @classmethod
    def from_string(cls, education_str: str) -> 'EducationLevel':
        """
        Convertit une chaîne en niveau d'éducation.
        
        Args:
            education_str: Chaîne représentant le niveau d'éducation
            
        Returns:
            Niveau d'éducation correspondant
            
        Raises:
            ValueError: Si la chaîne n'est pas reconnue
        """
        education_lower = education_str.lower().strip()
        
        # Mappings pour différentes variantes
        mappings = {
            'none': cls.NONE,
            'no education': cls.NONE,
            'high school': cls.HIGH_SCHOOL,
            'secondary': cls.HIGH_SCHOOL,
            'bac': cls.HIGH_SCHOOL,
            'associate': cls.ASSOCIATE,
            'technical': cls.ASSOCIATE,
            'diploma': cls.ASSOCIATE,
            'bachelor': cls.BACHELOR,
            "bachelor's": cls.BACHELOR,
            'licence': cls.BACHELOR,
            'master': cls.MASTER,
            "master's": cls.MASTER,
            'phd': cls.PHD,
            'doctorate': cls.PHD,
            'doctoral': cls.PHD
        }
        
        # Recherche exacte
        if education_lower in mappings:
            return mappings[education_lower]
        
        # Recherche partielle
        for key, level in mappings.items():
            if key in education_lower:
                return level
        
        raise ValueError(f"Unknown education level: {education_str}")
    
    def meets_requirement(self, required_level: 'EducationLevel') -> bool:
        """
        Vérifie si ce niveau répond aux exigences.
        
        Args:
            required_level: Niveau requis
            
        Returns:
            True si ce niveau est égal ou supérieur au niveau requis
        """
        return self.level >= required_level.level
    
    def is_higher_than(self, other: 'EducationLevel') -> bool:
        """
        Vérifie si ce niveau est supérieur à un autre.
        
        Args:
            other: Autre niveau d'éducation
            
        Returns:
            True si ce niveau est supérieur
        """
        return self.level > other.level
    
    def gap_from(self, required_level: 'EducationLevel') -> int:
        """
        Calcule l'écart entre ce niveau et un niveau requis.
        
        Args:
            required_level: Niveau requis
            
        Returns:
            Différence en niveaux (positif si supérieur, négatif si inférieur)
        """
        return self.level - required_level.level
    
    @classmethod
    def get_all_levels(cls) -> List['EducationLevel']:
        """
        Retourne tous les niveaux d'éducation triés par ordre croissant.
        
        Returns:
            Liste des niveaux d'éducation
        """
        return sorted(list(cls), key=lambda x: x.level)
    
    def __str__(self) -> str:
        return self.description
    
    def __repr__(self) -> str:
        return f"EducationLevel.{self.name}"
    
    def __lt__(self, other):
        if not isinstance(other, EducationLevel):
            return NotImplemented
        return self.level < other.level
    
    def __le__(self, other):
        if not isinstance(other, EducationLevel):
            return NotImplemented
        return self.level <= other.level
    
    def __gt__(self, other):
        if not isinstance(other, EducationLevel):
            return NotImplemented
        return self.level > other.level
    
    def __ge__(self, other):
        if not isinstance(other, EducationLevel):
            return NotImplemented
        return self.level >= other.level
