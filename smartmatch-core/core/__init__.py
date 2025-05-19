"""
SmartMatcher Core Module
---------------------
Module central contenant les interfaces, modèles et exceptions
pour l'architecture modulaire du SmartMatcher.
"""

__version__ = "2.0.0"
__author__ = "Claude/Anthropic"

from .models import Candidate, Job, MatchResult, MatchInsight
from .interfaces import BaseMatchEngine, ScoringStrategy, CacheService
from .exceptions import SmartMatchError, ConfigurationError, ServiceError

__all__ = [
    'Candidate',
    'Job', 
    'MatchResult',
    'MatchInsight',
    'BaseMatchEngine',
    'ScoringStrategy',
    'CacheService',
    'SmartMatchError',
    'ConfigurationError',
    'ServiceError'
]
