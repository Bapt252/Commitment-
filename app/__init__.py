"""Module principal pour le système de matching Nexten SmartMatch"""

import logging
import os

# Configuration du logging
logging_level = os.environ.get('LOGGING_LEVEL', 'INFO')
logging.basicConfig(
    level=getattr(logging, logging_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import des composants principaux
from app.smartmatch import SmartMatchEngine
from app.semantic_analysis import SemanticAnalyzer
from app.data_loader import DataLoader
from app.insight_generator import InsightGenerator
from app.compat import GoogleMapsClient

# Version du système
__version__ = '1.0.0'

# Exports
__all__ = [
    'SmartMatchEngine',
    'SemanticAnalyzer',
    'DataLoader',
    'InsightGenerator',
    'GoogleMapsClient'
]