"""
Skill Value Objects

Représente les compétences et ensembles de compétences.
"""

from dataclasses import dataclass
from typing import Set, Iterator, List
from enum import Enum


class SkillCategory(Enum):
    """
    Catégories de compétences.
    """
    TECHNICAL = "technical"
    SOFT = "soft" 
    LANGUAGE = "language"
    TOOL = "tool"
    FRAMEWORK = "framework"
    METHODOLOGY = "methodology"


@dataclass(frozen=True)
class Skill:
    """
    Représente une compétence individuelle.
    """
    
    name: str
    category: SkillCategory
    synonyms: Set[str] = None
    
    def __post_init__(self):
        if self.synonyms is None:
            object.__setattr__(self, 'synonyms', set())
    
    def matches(self, other_skill_name: str) -> bool:
        """
        Vérifie si cette compétence correspond à un nom donné.
        
        Prend en compte les synonymes pour une correspondance flexible.
        
        Args:
            other_skill_name: Nom de la compétence à comparer
            
        Returns:
            True si les compétences correspondent
        """
        other_lower = other_skill_name.lower().strip()
        
        # Correspondance directe
        if self.name.lower() == other_lower:
            return True
            
        # Correspondance via synonymes
        return any(synonym.lower() == other_lower for synonym in self.synonyms)
    
    def __str__(self) -> str:
        return self.name
    
    def __hash__(self) -> int:
        return hash(self.name.lower())
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Skill):
            return False
        return self.name.lower() == other.name.lower()


@dataclass(frozen=True)
class SkillSet:
    """
    Représente un ensemble de compétences.
    """
    
    skills: Set[Skill]
    
    def __post_init__(self):
        if self.skills is None:
            object.__setattr__(self, 'skills', set())
    
    @classmethod
    def from_names(
        cls, 
        skill_names: List[str], 
        default_category: SkillCategory = SkillCategory.TECHNICAL
    ) -> 'SkillSet':
        """
        Crée un SkillSet à partir d'une liste de noms.
        
        Args:
            skill_names: Liste des noms de compétences
            default_category: Catégorie par défaut
            
        Returns:
            Nouvel objet SkillSet
        """
        skills = {Skill(name=name.strip(), category=default_category) 
                 for name in skill_names if name.strip()}
        return cls(skills=skills)
    
    def contains(self, skill_name: str) -> bool:
        """
        Vérifie si l'ensemble contient une compétence donnée.
        
        Args:
            skill_name: Nom de la compétence à rechercher
            
        Returns:
            True si la compétence est présente
        """
        return any(skill.matches(skill_name) for skill in self.skills)
    
    def intersection(self, other: 'SkillSet') -> 'SkillSet':
        """
        Retourne l'intersection avec un autre ensemble de compétences.
        
        Args:
            other: Autre ensemble de compétences
            
        Returns:
            Nouvel ensemble contenant les compétences communes
        """
        matching_skills = set()
        
        for skill in self.skills:
            for other_skill in other.skills:
                if skill.matches(other_skill.name):
                    matching_skills.add(skill)
                    break
        
        return SkillSet(skills=matching_skills)
    
    def union(self, other: 'SkillSet') -> 'SkillSet':
        """
        Retourne l'union avec un autre ensemble de compétences.
        
        Args:
            other: Autre ensemble de compétences
            
        Returns:
            Nouvel ensemble contenant toutes les compétences
        """
        all_skills = self.skills.union(other.skills)
        return SkillSet(skills=all_skills)
    
    def difference(self, other: 'SkillSet') -> 'SkillSet':
        """
        Retourne les compétences présentes dans cet ensemble mais pas dans l'autre.
        
        Args:
            other: Autre ensemble de compétences
            
        Returns:
            Nouvel ensemble contenant la différence
        """
        differing_skills = set()
        
        for skill in self.skills:
            found = False
            for other_skill in other.skills:
                if skill.matches(other_skill.name):
                    found = True
                    break
            if not found:
                differing_skills.add(skill)
        
        return SkillSet(skills=differing_skills)
    
    def get_by_category(self, category: SkillCategory) -> 'SkillSet':
        """
        Retourne les compétences d'une catégorie spécifique.
        
        Args:
            category: Catégorie de compétences
            
        Returns:
            Nouvel ensemble contenant les compétences de la catégorie
        """
        category_skills = {skill for skill in self.skills if skill.category == category}
        return SkillSet(skills=category_skills)
    
    def to_names(self) -> List[str]:
        """
        Convertit l'ensemble en liste de noms de compétences.
        
        Returns:
            Liste des noms de compétences
        """
        return [skill.name for skill in self.skills]
    
    def is_empty(self) -> bool:
        """
        Vérifie si l'ensemble est vide.
        
        Returns:
            True si aucune compétence n'est présente
        """
        return len(self.skills) == 0
    
    def size(self) -> int:
        """
        Retourne le nombre de compétences.
        
        Returns:
            Nombre de compétences
        """
        return len(self.skills)
    
    def __iter__(self) -> Iterator[Skill]:
        return iter(self.skills)
    
    def __len__(self) -> int:
        return len(self.skills)
    
    def __str__(self) -> str:
        skill_names = ", ".join(skill.name for skill in sorted(self.skills, key=lambda s: s.name))
        return f"SkillSet([{skill_names}])"
    
    def __repr__(self) -> str:
        return self.__str__()
