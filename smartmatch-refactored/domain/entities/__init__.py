"""
Domain Entities

Entités métier représentant les concepts centraux du domaine de matching.
"""

from .candidate import Candidate
from .job_offer import JobOffer
from .match_result import MatchResult

__all__ = [
    'Candidate',
    'JobOffer', 
    'MatchResult'
]
