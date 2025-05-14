"""
Module de compatibilité pour Nexten SmartMatch
---------------------------------------------
Ce module contient des utilitaires pour assurer la compatibilité avec
différentes configurations et environnements.
"""

import os
import logging
import importlib.util

# Configuration du logging
logger = logging.getLogger(__name__)

# Vérifier la disponibilité des dépendances optionnelles
DEPENDENCIES = {
    'sklearn': {
        'package': 'scikit-learn',
        'available': False,
        'import_name': 'sklearn'
    },
    'nltk': {
        'package': 'nltk',
        'available': False,
        'import_name': 'nltk'
    },
    'pandas': {
        'package': 'pandas',
        'available': False,
        'import_name': 'pandas'
    },
    'requests': {
        'package': 'requests',
        'available': False,
        'import_name': 'requests'
    },
    'matplotlib': {
        'package': 'matplotlib',
        'available': False,
        'import_name': 'matplotlib'
    }
}

# Vérifier quelles dépendances sont disponibles
for name, info in DEPENDENCIES.items():
    try:
        spec = importlib.util.find_spec(info['import_name'])
        if spec is not None:
            DEPENDENCIES[name]['available'] = True
            logger.debug(f"Dépendance {name} disponible")
        else:
            logger.warning(f"Dépendance {name} non disponible")
    except ImportError:
        logger.warning(f"Dépendance {name} non disponible")

# Exposer une fonction pour vérifier les dépendances
def check_dependencies():
    """
    Vérifie que toutes les dépendances nécessaires sont disponibles
    
    Returns:
        dict: État des dépendances
    """
    return DEPENDENCIES

# Fonction pour vérifier la clé API Google Maps
def validate_google_maps_key(api_key=None):
    """
    Vérifie la validité d'une clé API Google Maps
    
    Args:
        api_key (str, optional): Clé API à vérifier, sinon utilise la variable d'environnement
        
    Returns:
        bool: True si la clé est valide, sinon False
    """
    key = api_key or os.environ.get('GOOGLE_MAPS_API_KEY')
    
    if not key:
        logger.warning("Aucune clé API Google Maps trouvée")
        return False
    
    # Valider le format basique de la clé (commence généralement par "AIza")
    if not key.startswith("AIza"):
        logger.warning("Format de clé API Google Maps incorrect")
        return False
    
    # Pour une validation plus complète, il faudrait faire une requête test à l'API
    # Mais cela consommerait inutilement un quota
    
    return True

# Variables globales de configuration
DEFAULT_CONFIG = {
    'use_google_maps': True,
    'use_cache': True,
    'cache_size': 1000,
    'min_match_threshold': 0.6,
    'weights': {
        'skills': 0.40,
        'location': 0.25,
        'experience': 0.15,
        'education': 0.10,
        'preferences': 0.10
    }
}

# Fonction pour obtenir la configuration
def get_config():
    """
    Obtient la configuration actuelle
    
    Returns:
        dict: Configuration actuelle
    """
    return DEFAULT_CONFIG