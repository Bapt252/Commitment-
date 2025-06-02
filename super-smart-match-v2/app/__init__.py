"""
SuperSmartMatch V2 - Application Package

Service unifié intelligent pour le matching candidat-offre
Intègre Nexten Matcher et algorithmes V1 existants
"""

__version__ = "2.0.0"
__author__ = "SuperSmartMatch Team"
__description__ = "Service unifié intelligent de matching"

# Configuration des logs pour le package
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())