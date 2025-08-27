"""
Domain Value Objects

Objets valeur immutables représentant des concepts sans identité.
"""

from .skills import SkillSet, Skill
from .location import Location
from .experience import ExperienceLevel, ExperienceRange
from .education import EducationLevel
from .preferences import CandidatePreferences
from .requirements import JobRequirements
from .salary import SalaryRange
from .scores import OverallScore, DetailedScores, SkillScore, LocationScore
from .insights import MatchInsight, InsightType, InsightCategory

__all__ = [
    'SkillSet', 
    'Skill',
    'Location',
    'ExperienceLevel',
    'ExperienceRange', 
    'EducationLevel',
    'CandidatePreferences',
    'JobRequirements',
    'SalaryRange',
    'OverallScore',
    'DetailedScores',
    'SkillScore',
    'LocationScore',
    'MatchInsight',
    'InsightType',
    'InsightCategory'
]
