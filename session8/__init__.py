"""
Module d'analyse comportementale et de profilage utilisateur pour Commitment.

Ce package contient tous les composants nécessaires pour l'analyse comportementale
et le profilage des utilisateurs, avec intégration au système de tracking existant.
"""

from session8.feature_extractor import FeatureExtractor
from session8.profile_manager import ProfileManager
from session8.user_clustering import UserClustering
from session8.pattern_detector import PatternDetector
from session8.preference_calculator import PreferenceCalculator
from session8.tracking_integration import TrackingIntegration
from session8.visualizations import Visualizations
from session8.config import CONFIG
import session8.api

__all__ = [
    'FeatureExtractor',
    'ProfileManager',
    'UserClustering',
    'PatternDetector',
    'PreferenceCalculator',
    'TrackingIntegration',
    'Visualizations',
    'CONFIG',
    'api'
]

__version__ = '1.0.0'
