#!/usr/bin/env python3
"""
Session 6: Hungarian Algorithm Module
=============================================

Module central pour l'algorithme hongrois et le matching optimal.
Intègre avec les Sessions 4 et 5 pour un matching avancé.

🎯 Fonctionnalités principales:
- Algorithme hongrois optimisé
- Génération intelligente de matrices de coûts
- Système de contraintes flexibles
- Matching bidirectionnel
"""

__version__ = "1.0.0"
__session__ = "6"

# Core algorithm exports
from .algorithm import HungarianAlgorithm
from .cost_matrix import CostMatrixGenerator
from .constraint_system import ConstraintSystem, HardConstraint, SoftConstraint
from .bidirectional_matcher import BidirectionalMatcher

# Main interface
from .algorithm import solve_assignment_problem

__all__ = [
    # Core classes
    'HungarianAlgorithm',
    'CostMatrixGenerator', 
    'ConstraintSystem',
    'BidirectionalMatcher',
    
    # Constraint types
    'HardConstraint',
    'SoftConstraint',
    
    # Main function
    'solve_assignment_problem'
]

# Module configuration
CONFIG = {
    'default_algorithm': 'scipy',  # 'scipy' or 'custom'
    'max_matrix_size': 10000,
    'memory_efficient': True,
    'enable_constraints': True,
    'bidirectional_mode': True
}

# Integration avec Session 4 (Enhanced Skills Matcher)
try:
    from ..matchers.enhanced_skills_matcher import EnhancedSkillsMatcher
    CONFIG['skills_matcher_available'] = True
except ImportError:
    CONFIG['skills_matcher_available'] = False

# Integration avec Session 5 (ML Optimization)
try:
    from ..optimizers.ml_optimizer import MLOptimizer
    CONFIG['ml_optimizer_available'] = True
except ImportError:
    CONFIG['ml_optimizer_available'] = False

print(f"🎯 Session 6 Hungarian Module loaded (v{__version__})")
print(f"   Skills Matcher: {'✅' if CONFIG['skills_matcher_available'] else '❌'}")
print(f"   ML Optimizer: {'✅' if CONFIG['ml_optimizer_available'] else '❌'}")
