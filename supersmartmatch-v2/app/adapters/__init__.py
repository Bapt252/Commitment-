"""
Adaptateurs pour services externes SuperSmartMatch V2

Adaptateurs pour intégrer les services externes :
- Nexten Matcher (port 5052) - 40K lignes ML
- SuperSmartMatch V1 (port 5062) - 4 algorithmes

Gestion unifiée des formats de données et des réponses.
"""

from .nexten_adapter import NextenMatcherAdapter
from .supersmartmatch_v1_adapter import SuperSmartMatchV1Adapter

__all__ = [
    "NextenMatcherAdapter",
    "SuperSmartMatchV1Adapter"
]
