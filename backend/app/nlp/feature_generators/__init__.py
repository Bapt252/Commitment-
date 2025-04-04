"""
Générateurs de features pour le moteur de matching avancé.
Ce package contient des générateurs spécialisés pour différents types de features
utilisées dans le système de matching XGBoost.
"""

from .skills_features import SkillsFeatureGenerator
from .cultural_features import CulturalAlignmentGenerator
from .textual_features import TextualSimilarityGenerator
from .preference_features import PreferenceFeatureGenerator

__all__ = [
    'SkillsFeatureGenerator',
    'CulturalAlignmentGenerator', 
    'TextualSimilarityGenerator',
    'PreferenceFeatureGenerator'
]
