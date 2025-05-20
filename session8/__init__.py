\"\"\"
Module d'analyse comportementale et de profiling utilisateur pour le projet Commitment.

Ce module regroupe les composants pour l'analyse comportementale et le profiling des
utilisateurs, intégré avec le système de tracking existant.
\"\"\"

from .feature_extractor import FeatureExtractor
from .profile_manager import ProfileManager
from .user_clustering import UserClustering
from .pattern_detector import PatternDetector
from .preference_calculator import PreferenceCalculator
from .enriched_profiles_api import EnrichedProfilesAPI
from .tracking_integration import TrackingIntegration
from .behavior_visualization import BehaviorVisualization
from .config import default_config

def setup_profiling_system(config=None):
    """
    Configure et initialise tous les composants du système de profilage.
    
    Args:
        config: Configuration personnalisée (optionnelle)
        
    Returns:
        Dict contenant tous les composants initialisés
    """
    # Initialisation de la configuration
    system_config = default_config.copy()
    if config:
        system_config.update(config)
    
    # Création des composants
    feature_extractor = FeatureExtractor()
    profile_manager = ProfileManager()
    pattern_detector = PatternDetector()
    user_clustering = UserClustering(
        profile_manager=profile_manager,
        pattern_detector=pattern_detector
    )
    preference_calculator = PreferenceCalculator(
        profile_manager=profile_manager,
        pattern_detector=pattern_detector
    )
    tracking_integration = TrackingIntegration(
        profile_manager=profile_manager,
        feature_extractor=feature_extractor,
        pattern_detector=pattern_detector,
        preference_calculator=preference_calculator,
        user_clustering=user_clustering,
        config=system_config.get("tracking_integration", {})
    )
    enriched_profiles_api = EnrichedProfilesAPI(
        profile_manager=profile_manager,
        preference_calculator=preference_calculator,
        user_clustering=user_clustering,
        pattern_detector=pattern_detector,
        config=system_config.get("enriched_profiles_api", {})
    )
    behavior_visualization = BehaviorVisualization(
        user_clustering=user_clustering,
        pattern_detector=pattern_detector,
        profile_manager=profile_manager,
        preference_calculator=preference_calculator,
        config=system_config.get("behavior_visualization", {})
    )
    
    # Retourner tous les composants
    return {
        "feature_extractor": feature_extractor,
        "profile_manager": profile_manager,
        "user_clustering": user_clustering,
        "pattern_detector": pattern_detector,
        "preference_calculator": preference_calculator,
        "tracking_integration": tracking_integration,
        "api": enriched_profiles_api,
        "visualizer": behavior_visualization
    }
