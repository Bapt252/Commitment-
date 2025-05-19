#!/usr/bin/env python3
"""
Session 6: Advanced Constraint System
====================================

Système de contraintes flexible pour le matching optimal.
Support contraintes hard (éliminatoires) et soft (pénalités).

🔥 Fonctionnalités:
- Contraintes hard: Éliminent les assignments impossibles
- Contraintes soft: Ajoutent des pénalités à la matrice de coûts
- Contraintes métier prédéfinies (salaire, localisation, etc.)
- Contraintes personnalisées dynamiques
- Validation en temps réel
"""

import numpy as np
import logging
from typing import List, Dict, Any, Optional, Callable, Tuple, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import re

# Configuration du logging
logger = logging.getLogger(__name__)

class ConstraintType(Enum):
    """Types de contraintes."""
    HARD = "hard"  # Éliminatoire
    SOFT = "soft"  # Pénalité

class ConstraintPriority(Enum):
    """Priorités des contraintes."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class ConstraintResult:
    """Résultat de l'évaluation d'une contrainte."""
    satisfied: bool
    penalty: float = 0.0
    message: str = ""
    
    def __post_init__(self):
        """Validation des résultats."""
        if self.satisfied and self.penalty > 0:
            logger.warning("Constraint satisfied but penalty > 0")

class BaseConstraint(ABC):
    """Classe de base pour les contraintes."""
    
    def __init__(self, 
                 name: str,
                 constraint_type: ConstraintType,
                 priority: ConstraintPriority = ConstraintPriority.MEDIUM,
                 description: str = ""):
        self.name = name
        self.constraint_type = constraint_type
        self.priority = priority
        self.description = description
        self.enabled = True
        
    @abstractmethod
    def evaluate(self, candidate: Any, job: Any) -> ConstraintResult:
        """Évalue la contrainte pour une paire candidat-job."""
        pass
    
    def disable(self) -> None:
        """Désactive la contrainte."""
        self.enabled = False
        logger.info(f"Constraint '{self.name}' disabled")
    
    def enable(self) -> None:
        """Active la contrainte."""
        self.enabled = True
        logger.info(f"Constraint '{self.name}' enabled")
    
    def __str__(self) -> str:
        status = "enabled" if self.enabled else "disabled"
        return f"{self.name} ({self.constraint_type.value}, {status})"

class HardConstraint(BaseConstraint):
    """Contrainte hard (éliminatoire)."""
    
    def __init__(self, name: str, **kwargs):
        super().__init__(name, ConstraintType.HARD, **kwargs)

class SoftConstraint(BaseConstraint):
    """Contrainte soft (pénalité)."""
    
    def __init__(self, 
                 name: str, 
                 max_penalty: float = 1.0,
                 **kwargs):
        super().__init__(name, ConstraintType.SOFT, **kwargs)
        self.max_penalty = max_penalty
    
    def calculate_penalty(self, violation_degree: float) -> float:
        """Calcule la pénalité basée sur le degré de violation."""
        return min(self.max_penalty, violation_degree * self.max_penalty)

# ===========================================
# CONTRAINTES PRÉDÉFINIES
# ===========================================

class SalaryRangeConstraint(BaseConstraint):
    """Contrainte sur la fourchette salariale."""
    
    def __init__(self, 
                 constraint_type: ConstraintType = ConstraintType.SOFT,
                 tolerance_percent: float = 0.1):
        super().__init__(
            name="salary_range",
            constraint_type=constraint_type,
            description="Vérifie la compatibilité salariale"
        )
        self.tolerance_percent = tolerance_percent
    
    def evaluate(self, candidate: Any, job: Any) -> ConstraintResult:
        """Évalue la contrainte salariale."""
        if not hasattr(candidate, 'salary_expectation') or not candidate.salary_expectation:
            return ConstraintResult(satisfied=True, message="No salary expectation")
        
        if not hasattr(job, 'salary_range') or not job.salary_range:
            return ConstraintResult(satisfied=True, message="No salary range defined")
        
        expectation = candidate.salary_expectation
        min_salary, max_salary = job.salary_range
        
        # Tolérance sur la fourchette
        tolerance = self.tolerance_percent
        adjusted_min = min_salary * (1 - tolerance)
        adjusted_max = max_salary * (1 + tolerance)
        
        if adjusted_min <= expectation <= adjusted_max:
            return ConstraintResult(satisfied=True, message="Salary compatible")
        
        # Calcul de la violation
        if expectation < adjusted_min:
            violation = (adjusted_min - expectation) / adjusted_min
            penalty = violation if self.constraint_type == ConstraintType.SOFT else 0
            return ConstraintResult(
                satisfied=False,
                penalty=penalty,
                message=f"Salary too low: {expectation} < {adjusted_min}"
            )
        else:
            violation = (expectation - adjusted_max) / adjusted_max
            penalty = violation if self.constraint_type == ConstraintType.SOFT else 0
            return ConstraintResult(
                satisfied=False,
                penalty=penalty,
                message=f"Salary too high: {expectation} > {adjusted_max}"
            )

class ExperienceRequirementConstraint(BaseConstraint):
    """Contrainte sur l'expérience requise."""
    
    def __init__(self, 
                 constraint_type: ConstraintType = ConstraintType.HARD,
                 allow_overqualification: bool = True):
        super().__init__(
            name="experience_requirement",
            constraint_type=constraint_type,
            description="Vérifie l'expérience minimale requise"
        )
        self.allow_overqualification = allow_overqualification
    
    def evaluate(self, candidate: Any, job: Any) -> ConstraintResult:
        """Évalue la contrainte d'expérience."""
        if not hasattr(candidate, 'experience_years'):
            return ConstraintResult(satisfied=True, message="No experience data")
        
        if not hasattr(job, 'min_experience'):
            return ConstraintResult(satisfied=True, message="No experience requirement")
        
        candidate_exp = candidate.experience_years
        min_exp = job.min_experience
        max_exp = getattr(job, 'max_experience', None)
        
        # Vérification expérience minimale
        if candidate_exp < min_exp:
            deficit = min_exp - candidate_exp
            penalty = deficit / max(min_exp, 1.0) if self.constraint_type == ConstraintType.SOFT else 0
            return ConstraintResult(
                satisfied=False,
                penalty=penalty,
                message=f"Insufficient experience: {candidate_exp} < {min_exp}"
            )
        
        # Vérification surqualification
        if max_exp and candidate_exp > max_exp and not self.allow_overqualification:
            excess = candidate_exp - max_exp
            penalty = excess / max_exp if self.constraint_type == ConstraintType.SOFT else 0
            return ConstraintResult(
                satisfied=False,
                penalty=penalty * 0.5,  # Pénalité plus faible pour surqualification
                message=f"Overqualified: {candidate_exp} > {max_exp}"
            )
        
        return ConstraintResult(satisfied=True, message="Experience compatible")

class RequiredSkillsConstraint(BaseConstraint):
    """Contrainte sur les compétences obligatoires."""
    
    def __init__(self, 
                 constraint_type: ConstraintType = ConstraintType.HARD,
                 minimum_match_ratio: float = 0.7):
        super().__init__(
            name="required_skills",
            constraint_type=constraint_type,
            description="Vérifie les compétences obligatoires"
        )
        self.minimum_match_ratio = minimum_match_ratio
    
    def evaluate(self, candidate: Any, job: Any) -> ConstraintResult:
        """Évalue la contrainte des compétences."""
        if not hasattr(candidate, 'skills') or not candidate.skills:
            return ConstraintResult(satisfied=False, message="No candidate skills")
        
        if not hasattr(job, 'required_skills') or not job.required_skills:
            return ConstraintResult(satisfied=True, message="No skills required")
        
        candidate_skills = set(skill.lower() for skill in candidate.skills)
        required_skills = set(skill.lower() for skill in job.required_skills)
        
        # Calcul du ratio de correspondance
        matched_skills = candidate_skills & required_skills
        match_ratio = len(matched_skills) / len(required_skills)
        
        if match_ratio >= self.minimum_match_ratio:
            return ConstraintResult(satisfied=True, message=f"Skills match: {match_ratio:.2%}")
        
        # Contrainte non satisfaite
        deficit = self.minimum_match_ratio - match_ratio
        penalty = deficit if self.constraint_type == ConstraintType.SOFT else 0
        
        missing_skills = required_skills - candidate_skills
        return ConstraintResult(
            satisfied=False,
            penalty=penalty,
            message=f"Missing skills: {missing_skills}"
        )

class LocationConstraint(BaseConstraint):
    """Contrainte sur la localisation."""
    
    def __init__(self, 
                 constraint_type: ConstraintType = ConstraintType.SOFT,
                 allow_remote: bool = True,
                 max_distance_km: Optional[float] = None):
        super().__init__(
            name="location",
            constraint_type=constraint_type,
            description="Vérifie la compatibilité géographique"
        )
        self.allow_remote = allow_remote
        self.max_distance_km = max_distance_km
    
    def evaluate(self, candidate: Any, job: Any) -> ConstraintResult:
        """Évalue la contrainte de localisation."""
        if not hasattr(candidate, 'location') or not candidate.location:
            return ConstraintResult(satisfied=True, message="No candidate location")
        
        if not hasattr(job, 'location') or not job.location:
            return ConstraintResult(satisfied=True, message="No job location")
        
        candidate_location = candidate.location.lower()
        job_location = job.location.lower()
        
        # Vérification remote
        if self.allow_remote and ('remote' in job_location or 'distance' in job_location):
            return ConstraintResult(satisfied=True, message="Remote work allowed")
        
        # Correspondance exacte
        if candidate_location == job_location:
            return ConstraintResult(satisfied=True, message="Location match")
        
        # Correspondance partielle (même ville/région)
        candidate_parts = set(part.strip() for part in candidate_location.split(','))
        job_parts = set(part.strip() for part in job_location.split(','))
        
        if candidate_parts & job_parts:
            return ConstraintResult(satisfied=True, message="Partial location match")
        
        # Aucune correspondance
        penalty = 0.8 if self.constraint_type == ConstraintType.SOFT else 0
        return ConstraintResult(
            satisfied=False,
            penalty=penalty,
            message=f"Location mismatch: {candidate_location} != {job_location}"
        )

class EducationRequirementConstraint(BaseConstraint):
    """Contrainte sur le niveau d'éducation."""
    
    def __init__(self, constraint_type: ConstraintType = ConstraintType.SOFT):
        super().__init__(
            name="education_requirement",
            constraint_type=constraint_type,
            description="Vérifie le niveau d'éducation requis"
        )
        
        # Hiérarchie des niveaux d'éducation
        self.education_levels = {
            'high_school': 1,
            'associate': 2,
            'bachelor': 3,
            'master': 4,
            'phd': 5
        }
    
    def evaluate(self, candidate: Any, job: Any) -> ConstraintResult:
        """Évalue la contrainte d'éducation."""
        if not hasattr(candidate, 'education_level') or not candidate.education_level:
            return ConstraintResult(satisfied=True, message="No candidate education")
        
        if not hasattr(job, 'education_required') or not job.education_required:
            return ConstraintResult(satisfied=True, message="No education requirement")
        
        candidate_level = self.education_levels.get(candidate.education_level.lower(), 0)
        required_level = self.education_levels.get(job.education_required.lower(), 0)
        
        if candidate_level >= required_level:
            return ConstraintResult(satisfied=True, message="Education requirement met")
        
        # Éducation insuffisante
        deficit = required_level - candidate_level
        penalty = deficit / 5.0 if self.constraint_type == ConstraintType.SOFT else 0
        
        return ConstraintResult(
            satisfied=False,
            penalty=penalty,
            message=f"Education insufficient: {candidate.education_level} < {job.education_required}"
        )

class LanguageRequirementConstraint(BaseConstraint):
    """Contrainte sur les langues requises."""
    
    def __init__(self, constraint_type: ConstraintType = ConstraintType.HARD):
        super().__init__(
            name="language_requirement",
            constraint_type=constraint_type,
            description="Vérifie les langues requises"
        )
    
    def evaluate(self, candidate: Any, job: Any) -> ConstraintResult:
        """Évalue la contrainte des langues."""
        if not hasattr(candidate, 'languages') or not candidate.languages:
            candidate_languages = set()
        else:
            candidate_languages = set(lang.lower() for lang in candidate.languages)
        
        if not hasattr(job, 'languages_required') or not job.languages_required:
            return ConstraintResult(satisfied=True, message="No language requirement")
        
        required_languages = set(lang.lower() for lang in job.languages_required)
        
        # Vérification des langues requises
        missing_languages = required_languages - candidate_languages
        
        if not missing_languages:
            return ConstraintResult(satisfied=True, message="All languages available")
        
        # Langues manquantes
        coverage = len(required_languages & candidate_languages) / len(required_languages)
        penalty = (1 - coverage) if self.constraint_type == ConstraintType.SOFT else 0
        
        return ConstraintResult(
            satisfied=False,
            penalty=penalty,
            message=f"Missing languages: {missing_languages}"
        )

class CustomConstraint(BaseConstraint):
    """Contrainte personnalisée avec fonction d'évaluation."""
    
    def __init__(self, 
                 name: str,
                 evaluation_function: Callable[[Any, Any], ConstraintResult],
                 constraint_type: ConstraintType = ConstraintType.SOFT,
                 **kwargs):
        super().__init__(name, constraint_type, **kwargs)
        self.evaluation_function = evaluation_function
    
    def evaluate(self, candidate: Any, job: Any) -> ConstraintResult:
        """Évalue avec la fonction personnalisée."""
        try:
            return self.evaluation_function(candidate, job)
        except Exception as e:
            logger.error(f"Custom constraint '{self.name}' failed: {e}")
            return ConstraintResult(satisfied=True, message=f"Evaluation failed: {e}")

# ===========================================
# SYSTÈME DE CONTRAINTES PRINCIPAL
# ===========================================

class ConstraintSystem:
    """Système principal de gestion des contraintes."""
    
    def __init__(self):
        self.constraints: List[BaseConstraint] = []
        self.violation_threshold = 0.5  # Seuil pour hard constraints en mode soft
        
        logger.info("ConstraintSystem initialized")
    
    def add_constraint(self, constraint: BaseConstraint) -> None:
        """Ajoute une contrainte au système."""
        # Vérifier les doublons
        existing_names = [c.name for c in self.constraints]
        if constraint.name in existing_names:
            logger.warning(f"Constraint '{constraint.name}' already exists, replacing")
            self.remove_constraint(constraint.name)
        
        self.constraints.append(constraint)
        logger.info(f"Added constraint: {constraint}")
    
    def remove_constraint(self, name: str) -> bool:
        """Supprime une contrainte par nom."""
        for i, constraint in enumerate(self.constraints):
            if constraint.name == name:
                removed = self.constraints.pop(i)\n                logger.info(f"Removed constraint: {removed}")
                return True
        logger.warning(f"Constraint '{name}' not found")
        return False
    
    def get_constraint(self, name: str) -> Optional[BaseConstraint]:
        """Récupère une contrainte par nom."""
        for constraint in self.constraints:
            if constraint.name == name:
                return constraint
        return None
    
    def evaluate_pair(self, candidate: Any, job: Any) -> Tuple[bool, float, List[str]]:
        """
        Évalue toutes les contraintes pour une paire candidat-job.
        
        Returns:
            Tuple (is_valid, total_penalty, violation_messages)
        """
        is_valid = True
        total_penalty = 0.0
        violation_messages = []
        
        for constraint in self.constraints:
            if not constraint.enabled:
                continue
            
            result = constraint.evaluate(candidate, job)
            
            if not result.satisfied:
                if constraint.constraint_type == ConstraintType.HARD:
                    is_valid = False
                    violation_messages.append(f"HARD: {result.message}")
                else:
                    total_penalty += result.penalty
                    if result.penalty > self.violation_threshold:
                        violation_messages.append(f"SOFT: {result.message} (penalty={result.penalty:.2f})")
        
        return is_valid, total_penalty, violation_messages
    
    def apply_to_cost_matrix(self, 
                           cost_matrix: np.ndarray,
                           candidates: List[Any],
                           jobs: List[Any]) -> np.ndarray:
        """
        Applique les contraintes à une matrice de coûts.
        
        Args:
            cost_matrix: Matrice de coûts originale
            candidates: Liste des candidats
            jobs: Liste des jobs
            
        Returns:
            Matrice de coûts modifiée
        """
        modified_matrix = cost_matrix.copy()
        hard_constraint_penalty = 1e6  # Très haute pénalité pour contraintes hard
        
        logger.info(f"Applying {len(self.constraints)} constraints to {cost_matrix.shape} matrix")
        
        for i, candidate in enumerate(candidates):
            for j, job in enumerate(jobs):
                is_valid, penalty, messages = self.evaluate_pair(candidate, job)
                
                if not is_valid:
                    # Contrainte hard violée
                    modified_matrix[i, j] = hard_constraint_penalty
                else:
                    # Ajout des pénalités soft
                    modified_matrix[i, j] += penalty
        
        # Statistiques
        hard_violations = np.sum(modified_matrix >= hard_constraint_penalty)
        soft_penalties = np.sum(modified_matrix != cost_matrix) - hard_violations
        
        logger.info(f"Constraints applied: {hard_violations} hard violations, {soft_penalties} soft penalties")
        
        return modified_matrix
    
    def get_constraint_summary(self) -> Dict[str, Any]:
        """Retourne un résumé des contraintes."""
        summary = {
            'total_constraints': len(self.constraints),
            'enabled_constraints': len([c for c in self.constraints if c.enabled]),
            'hard_constraints': len([c for c in self.constraints if c.constraint_type == ConstraintType.HARD]),
            'soft_constraints': len([c for c in self.constraints if c.constraint_type == ConstraintType.SOFT]),
            'constraints': []
        }
        
        for constraint in self.constraints:
            summary['constraints'].append({
                'name': constraint.name,
                'type': constraint.constraint_type.value,
                'priority': constraint.priority.value,
                'enabled': constraint.enabled,
                'description': constraint.description
            })
        
        return summary
    
    def disable_all_constraints(self) -> None:
        """Désactive toutes les contraintes."""
        for constraint in self.constraints:
            constraint.disable()
        logger.info("All constraints disabled")
    
    def enable_all_constraints(self) -> None:
        """Active toutes les contraintes."""
        for constraint in self.constraints:
            constraint.enable()
        logger.info("All constraints enabled")
    
    def clear_constraints(self) -> None:
        """Supprime toutes les contraintes."""
        count = len(self.constraints)
        self.constraints.clear()
        logger.info(f"Cleared {count} constraints")

# ===========================================
# FACTORY POUR CONTRAINTES PRÉDÉFINIES
# ===========================================

class ConstraintFactory:
    """Factory pour créer des contraintes prédéfinies."""
    
    @staticmethod
    def create_standard_business_constraints() -> List[BaseConstraint]:
        """Crée un ensemble standard de contraintes métier."""
        constraints = [
            # Contraintes hard essentielles
            RequiredSkillsConstraint(
                constraint_type=ConstraintType.HARD,
                minimum_match_ratio=0.6
            ),
            ExperienceRequirementConstraint(
                constraint_type=ConstraintType.HARD,
                allow_overqualification=True
            ),
            LanguageRequirementConstraint(
                constraint_type=ConstraintType.HARD
            ),
            
            # Contraintes soft avec pénalités
            SalaryRangeConstraint(
                constraint_type=ConstraintType.SOFT,
                tolerance_percent=0.15
            ),
            LocationConstraint(
                constraint_type=ConstraintType.SOFT,
                allow_remote=True
            ),
            EducationRequirementConstraint(
                constraint_type=ConstraintType.SOFT
            )
        ]
        
        return constraints
    
    @staticmethod
    def create_relaxed_constraints() -> List[BaseConstraint]:
        """Crée des contraintes plus souples."""
        constraints = [
            # Toutes en soft avec seuils bas
            RequiredSkillsConstraint(
                constraint_type=ConstraintType.SOFT,
                minimum_match_ratio=0.3
            ),
            ExperienceRequirementConstraint(
                constraint_type=ConstraintType.SOFT,
                allow_overqualification=True
            ),
            SalaryRangeConstraint(
                constraint_type=ConstraintType.SOFT,
                tolerance_percent=0.25
            ),
            LocationConstraint(
                constraint_type=ConstraintType.SOFT,
                allow_remote=True
            )
        ]
        
        return constraints
    
    @staticmethod
    def create_strict_constraints() -> List[BaseConstraint]:
        """Crée des contraintes strictes."""
        constraints = [
            # Presque toutes en hard
            RequiredSkillsConstraint(
                constraint_type=ConstraintType.HARD,
                minimum_match_ratio=0.8
            ),
            ExperienceRequirementConstraint(
                constraint_type=ConstraintType.HARD,
                allow_overqualification=False
            ),
            LanguageRequirementConstraint(
                constraint_type=ConstraintType.HARD
            ),
            EducationRequirementConstraint(
                constraint_type=ConstraintType.HARD
            ),
            SalaryRangeConstraint(
                constraint_type=ConstraintType.SOFT,
                tolerance_percent=0.05
            )
        ]
        
        return constraints

# ===========================================
# FONCTIONS UTILITAIRES
# ===========================================

def create_sample_constraint_system() -> ConstraintSystem:
    """Crée un système de contraintes d'exemple."""
    system = ConstraintSystem()
    
    # Ajout des contraintes standard
    for constraint in ConstraintFactory.create_standard_business_constraints():
        system.add_constraint(constraint)
    
    return system

if __name__ == "__main__":
    # Test rapide
    print("🧪 Testing Constraint System")
    
    # Import des profils depuis cost_matrix pour les tests
    try:
        from .cost_matrix import CandidateProfile, JobProfile, create_sample_candidates, create_sample_jobs
        
        # Création d'exemples
        candidates = create_sample_candidates(3)
        jobs = create_sample_jobs(2)
        
        # Création du système de contraintes
        constraint_system = create_sample_constraint_system()
        
        print(f"Created {len(candidates)} candidates and {len(jobs)} jobs")
        print(f"Constraint system: {constraint_system.get_constraint_summary()}")
        
        # Test d'évaluation
        print("\n🔍 Evaluating constraints for each pair:")
        for i, candidate in enumerate(candidates):
            for j, job in enumerate(jobs):
                is_valid, penalty, messages = constraint_system.evaluate_pair(candidate, job)
                print(f"   {candidate.id} -> {job.id}: valid={is_valid}, penalty={penalty:.3f}")
                if messages:
                    for msg in messages[:2]:  # Limite à 2 messages
                        print(f"      {msg}")
        
        # Test sur matrice de coûts
        print("\n📊 Testing constraint application to cost matrix")
        original_matrix = np.random.rand(len(candidates), len(jobs))
        modified_matrix = constraint_system.apply_to_cost_matrix(original_matrix, candidates, jobs)
        
        print(f"Original matrix:\n{original_matrix}")
        print(f"Modified matrix:\n{modified_matrix}")
        
    except ImportError as e:
        print(f"⚠️  Cannot import cost_matrix module for testing: {e}")
        print("Testing constraint system without profiles...")
        
        # Test basique
        system = ConstraintSystem()
        system.add_constraint(CustomConstraint(
            name="test_constraint",
            evaluation_function=lambda c, j: ConstraintResult(satisfied=True, message="Test OK")
        ))
        
        print(f"Basic system created: {system.get_constraint_summary()}")
