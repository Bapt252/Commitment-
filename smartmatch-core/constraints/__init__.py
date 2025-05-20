#!/usr/bin/env python3
"""
Session 6: Constraints Module
=============================

Module spécialisé pour la gestion des contraintes métier dans le matching.
Architecture modulaire pour la définition, validation et application des contraintes.

🔥 Fonctionnalités:
- Contraintes de base abstraites
- Règles métier spécifiques
- Contraintes de performance
- Validation et application automatique
- Intégration avec le système Hungarian

Architecture:
- BaseConstraint: Classes abstraites de base
- BusinessRules: Règles métier prédéfinies
- PerformanceConstraints: Contraintes de performance
- ConstraintValidator: Système de validation
"""

__version__ = "1.0.0"
__session__ = "6"

# Core constraint exports
from .base_constraints import (
    BaseConstraint,
    HardConstraint,
    SoftConstraint,
    ConstraintResult,
    ConstraintType,
    ConstraintPriority
)

from .business_rules import (
    SalaryConstraint,
    ExperienceConstraint,
    SkillsConstraint,
    LocationConstraint,
    EducationConstraint,
    LanguageConstraint,
    AvailabilityConstraint,
    ContractTypeConstraint,
    IndustryConstraint
)

from .performance_constraints import (
    ExecutionTimeConstraint,
    MemoryUsageConstraint,
    ScalabilityConstraint,
    QualityThresholdConstraint,
    ConvergenceConstraint
)

from .constraint_validator import (
    ConstraintValidator,
    ValidationResult,
    ConstraintGroup,
    DependencyManager
)

__all__ = [
    # Base classes
    'BaseConstraint',
    'HardConstraint', 
    'SoftConstraint',
    'ConstraintResult',
    'ConstraintType',
    'ConstraintPriority',
    
    # Business rules
    'SalaryConstraint',
    'ExperienceConstraint',
    'SkillsConstraint',
    'LocationConstraint',
    'EducationConstraint',
    'LanguageConstraint',
    'AvailabilityConstraint',
    'ContractTypeConstraint',
    'IndustryConstraint',
    
    # Performance constraints
    'ExecutionTimeConstraint',
    'MemoryUsageConstraint',
    'ScalabilityConstraint',
    'QualityThresholdConstraint',
    'ConvergenceConstraint',
    
    # Validation system
    'ConstraintValidator',
    'ValidationResult',
    'ConstraintGroup',
    'DependencyManager'
]

# Configuration du module
CONFIG = {
    'strict_validation': True,
    'cache_evaluations': True,
    'parallel_evaluation': False,
    'max_constraint_depth': 10,
    'default_penalty_weight': 1.0
}

# Integration avec le module Hungarian
try:
    from ..hungarian.constraint_system import ConstraintSystem
    CONFIG['hungarian_integration'] = True
except ImportError:
    CONFIG['hungarian_integration'] = False

print(f"🚀 Session 6 Constraints Module loaded (v{__version__})")
print(f"   Hungarian Integration: {'✅' if CONFIG['hungarian_integration'] else '❌'}")
