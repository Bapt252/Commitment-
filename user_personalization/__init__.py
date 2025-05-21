"""
Module de personnalisation des matchs pour le projet Commitment.

Ce package contient les modules pour personnaliser les recommandations
en fonction des préférences et comportements des utilisateurs.
"""

__version__ = '1.0.0'

import os
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO if os.getenv('PERSONALIZATION_LOG_LEVEL') != 'DEBUG' else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Noms des modules disponibles
__all__ = [
    'weights',
    'collaborative',
    'cold_start',
    'temporal',
    'ab_testing',
    'matcher',
    'api'
]

logger.info(f"Module de personnalisation initialisé (version {__version__})")
