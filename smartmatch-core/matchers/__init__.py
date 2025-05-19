"""
SmartMatcher Matchers Module
---------------------------
Module contenant les différents matchers spécialisés pour l'évaluation
des critères de matching.
"""

from .base_matcher import BaseMatchEngine
from .skills_matcher import SkillsMatcher
from .location_matcher import LocationMatcher
from .experience_matcher import ExperienceMatcher
from .education_matcher import EducationMatcher
from .preference_matcher import PreferenceMatcher

__all__ = [
    'BaseMatchEngine',
    'SkillsMatcher',
    'LocationMatcher', 
    'ExperienceMatcher',
    'EducationMatcher',
    'PreferenceMatcher'
]
