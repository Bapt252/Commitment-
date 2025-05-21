"""
Module d'initialisation pour la personnalisation utilisateur (Session 10)
"""

import os
import logging
import colorlog

# Configuration du logger
def setup_logger():
    """Configure le logger pour le module de personnalisation."""
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    ))
    
    logger = colorlog.getLogger('user_personalization')
    logger.addHandler(handler)
    
    # Niveau de log basé sur l'environnement
    log_level = os.environ.get('LOG_LEVEL', 'INFO')
    logger.setLevel(getattr(logging, log_level))
    
    return logger

logger = setup_logger()

# Version du module
__version__ = '1.0.0'

# Constantes de configuration
DEFAULT_DATABASE_URL = os.environ.get(
    'DATABASE_URL', 
    'postgresql://postgres:postgres@localhost:5432/commitment'
)
API_PORT = int(os.environ.get('PERSONALIZATION_API_PORT', 5010))
API_HOST = os.environ.get('PERSONALIZATION_API_HOST', '0.0.0.0')
API_DEBUG = os.environ.get('PERSONALIZATION_API_DEBUG', 'false').lower() == 'true'

# Paramètres de personnalisation
COLLABORATIVE_FILTERING_ENABLED = True
COLD_START_ENABLED = True
TEMPORAL_WEIGHTING_ENABLED = True
AB_TESTING_ENABLED = True

# Poids par défaut pour le matching
DEFAULT_WEIGHTS = {
    'skills': 0.30,        # 30% pour les compétences
    'contract': 0.15,      # 15% pour le type de contrat
    'location': 0.20,      # 20% pour la localisation
    'date': 0.10,          # 10% pour la disponibilité
    'salary': 0.15,        # 15% pour le salaire
    'experience': 0.10,    # 10% pour l'expérience
    'soft_skills': 0.0,    # 0% pour les soft skills
    'culture': 0.0         # 0% pour la culture d'entreprise
}

# Paramètres pour le filtrage collaboratif
COLLABORATIVE_PARAMS = {
    'min_interactions': 5,        # Nombre minimum d'interactions pour considérer un utilisateur
    'num_similar_users': 10,      # Nombre d'utilisateurs similaires à considérer
    'num_factors': 50,            # Nombre de facteurs latents pour la factorisation matricielle
    'similarity_threshold': 0.3,  # Seuil de similarité minimum
}

# Paramètres pour le cold start
COLD_START_PARAMS = {
    'exploration_rate': 0.2,      # Taux d'exploration pour les nouveaux utilisateurs
    'transition_factor': 0.1,     # Facteur de transition vers le profil personnalisé
    'min_interactions': 10,       # Nombre minimum d'interactions pour sortir du cold start
}

# Paramètres pour la pondération temporelle
TEMPORAL_PARAMS = {
    'recency_factor': 0.8,        # Importance de la récence des actions
    'half_life_days': 30,         # Demi-vie des actions en jours
}

# Paramètres pour les tests A/B
AB_TEST_PARAMS = {
    'assignment_method': 'random',    # Méthode d'assignation aux groupes
    'control_group_size': 0.25,       # Taille du groupe de contrôle
}

logger.info(f"Module de personnalisation initialisé (v{__version__})")
