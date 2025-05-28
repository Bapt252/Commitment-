"""Module de compatibilité pour le projet Nexten SmartMatch.
Ce module regroupe les imports qui pourraient causer des problèmes de compatibilité.
"""

import logging
import os
import sys
import warnings

# Supprimer les warnings de compatibilité NumPy
warnings.filterwarnings("ignore", message=".*numpy.dtype size changed.*")
warnings.filterwarnings("ignore", message=".*A NumPy version.*")

# Ajouter le répertoire des modules personnalisés au path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

# Imports conditionnels pour la compatibilité
try:
    from app.google_maps_client import GoogleMapsClient
except ImportError:
    # Si le module n'est pas trouvé, importer une version de remplacement
    try:
        from app.compat.google_maps_client import GoogleMapsClient
    except ImportError:
        # Fallback basique
        class GoogleMapsClient:
            def __init__(self, *args, **kwargs):
                pass
            def get_distance(self, *args, **kwargs):
                return {"distance": 0, "duration": 0}

# Import TensorFlow avec gestion des erreurs de compatibilité NumPy
HAS_TENSORFLOW = False
tf = None
try:
    # Essayer d'importer TensorFlow sans déclencher l'erreur NumPy
    import importlib.util
    if importlib.util.find_spec("tensorflow") is not None:
        # Supprimer temporairement les warnings pendant l'import
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            import tensorflow as tf
            HAS_TENSORFLOW = True
            logging.info("TensorFlow importé avec succès")
except Exception as e:
    HAS_TENSORFLOW = False
    tf = None
    logging.warning(f"TensorFlow n'a pas pu être importé: {e}. Certaines fonctionnalités d'analyse sémantique avancées ne seront pas disponibles.")

# Import NLTK
try:
    import nltk
    HAS_NLTK = True
except ImportError:
    HAS_NLTK = False
    logging.warning("NLTK n'est pas installé. Certaines fonctionnalités de traitement du langage naturel ne seront pas disponibles.")

# Import scikit-learn
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    logging.warning("scikit-learn n'est pas installé. Les fonctionnalités d'analyse sémantique basiques utiliseront des alternatives.")

# Exports pour faciliter l'importation
__all__ = [
    'GoogleMapsClient',
    'HAS_TENSORFLOW',
    'HAS_NLTK', 
    'HAS_SKLEARN',
    'tf'
]
