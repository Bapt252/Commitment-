"""
Experience Value Objects

Représente l'expérience professionnelle et les gammes d'expérience.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ExperienceLevel(Enum):
    """
    Niveaux d'expérience standardisés.
    """
    ENTRY_LEVEL = (0, 2, "Entry Level")
    JUNIOR = (1, 3, "Junior")
    MID_LEVEL = (3, 5, "Mid Level")
    SENIOR = (5, 8, "Senior")
    EXPERT = (8, 15, "Expert")
    EXECUTIVE = (10, 30, "Executive")
    
    def __init__(self, min_years: int, max_years: int, label: str):
        self.min_years = min_years
        self.max_years = max_years
        self.label = label
    
    def contains(self, years: int) -> bool:
        """
        Vérifie si un nombre d'années d'expérience correspond à ce niveau.
        
        Args:
            years: Nombre d'années d'expérience
            
        Returns:
            True si l'expérience correspond au niveau
        """
        return self.min_years <= years <= self.max_years
    
    @classmethod
    def from_years(cls, years: int) -> 'ExperienceLevel':
        """
        Détermine le niveau d'expérience à partir du nombre d'années.
        
        Args:
            years: Nombre d'années d'expérience
            
        Returns:
            Niveau d'expérience correspondant
        """
        for level in cls:
            if level.contains(years):
                return level
        
        # Pour les valeurs extrêmes
        if years < 0:
            return cls.ENTRY_LEVEL
        else:
            return cls.EXECUTIVE
    
    def __str__(self) -> str:
        return f"{self.label} ({self.min_years}-{self.max_years} years)"


@dataclass(frozen=True)
class ExperienceRange:
    """
    Représente une gamme d'expérience requise pour un poste.
    """
    
    min_years: int
    max_years: Optional[int] = None
    
    def __post_init__(self):
        if self.min_years < 0:
            raise ValueError("Minimum years of experience cannot be negative")
        
        if self.max_years is not None and self.max_years < self.min_years:
            raise ValueError("Maximum years cannot be less than minimum years")
    
    @classmethod
    def exactly(cls, years: int) -> 'ExperienceRange':
        """
        Crée une gamme pour un nombre exact d'années.
        
        Args:
            years: Nombre exact d'années
            
        Returns:
            Gamme d'expérience pour ce nombre exact
        """
        return cls(min_years=years, max_years=years)
    
    @classmethod
    def minimum(cls, years: int) -> 'ExperienceRange':
        """
        Crée une gamme avec un minimum seulement.
        
        Args:
            years: Nombre minimum d'années
            
        Returns:
            Gamme d'expérience avec minimum seulement
        """
        return cls(min_years=years, max_years=None)
    
    @classmethod
    def between(cls, min_years: int, max_years: int) -> 'ExperienceRange':
        """
        Crée une gamme entre deux valeurs.
        
        Args:
            min_years: Nombre minimum d'années
            max_years: Nombre maximum d'années
            
        Returns:
            Gamme d'expérience entre les deux valeurs
        """
        return cls(min_years=min_years, max_years=max_years)
    
    def contains(self, years: int) -> bool:
        """
        Vérifie si un nombre d'années se trouve dans cette gamme.
        
        Args:
            years: Nombre d'années à vérifier
            
        Returns:
            True si les années sont dans la gamme
        """
        if years < self.min_years:
            return False
        
        if self.max_years is not None and years > self.max_years:
            return False
        
        return True
    
    def get_level(self) -> ExperienceLevel:
        """
        Retourne le niveau d'expérience correspondant à cette gamme.
        
        Utilise la valeur moyenne si une gamme est définie.
        
        Returns:
            Niveau d'expérience
        """
        if self.max_years is not None:
            avg_years = (self.min_years + self.max_years) / 2
            return ExperienceLevel.from_years(int(avg_years))
        else:
            return ExperienceLevel.from_years(self.min_years)
    
    def is_entry_level(self) -> bool:
        """
        Vérifie si cette gamme correspond à un niveau débutant.
        
        Returns:
            True si c'est un niveau débutant
        """
        return self.min_years <= 2
    
    def is_senior_level(self) -> bool:
        """
        Vérifie si cette gamme correspond à un niveau senior.
        
        Returns:
            True si c'est un niveau senior
        """
        return self.min_years >= 5
    
    def overlaps_with(self, other: 'ExperienceRange') -> bool:
        """
        Vérifie si cette gamme chevauche avec une autre.
        
        Args:
            other: Autre gamme d'expérience
            
        Returns:
            True si les gammes se chevauchent
        """
        # Si l'une des gammes n'a pas de maximum, on considère qu'elles se chevauchent
        # si l'autre commence avant que cette gamme ne se termine
        if self.max_years is None or other.max_years is None:
            return self.min_years <= (other.max_years or float('inf')) and \
                   other.min_years <= (self.max_years or float('inf'))
        
        # Gammes avec bornes définies
        return self.min_years <= other.max_years and other.min_years <= self.max_years
    
    def __str__(self) -> str:
        if self.max_years is not None:
            if self.min_years == self.max_years:
                return f"{self.min_years} years"
            else:
                return f"{self.min_years}-{self.max_years} years"
        else:
            return f"{self.min_years}+ years"
    
    def __repr__(self) -> str:
        return f"ExperienceRange({self.min_years}, {self.max_years})"
