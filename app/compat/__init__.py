"""Module de compatibilité pour le projet Nexten SmartMatch.
Ce module regroupe les imports qui pourraient causer des problèmes de compatibilité.
"""

import logging
import os
import sys

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
    from app.compat.google_maps_client import GoogleMapsClient

# Autres imports qui pourraient causer des problèmes de compatibilité
try:
    import tensorflow as tf
    HAS_TENSORFLOW = True
except ImportError:
    HAS_TENSORFLOW = False
    logging.warning("TensorFlow n'est pas installé. Certaines fonctionnalités d'analyse sémantique avancées ne seront pas disponibles.")

try:
    import nltk
    HAS_NLTK = True
except ImportError:
    HAS_NLTK = False
    logging.warning("NLTK n'est pas installé. Certaines fonctionnalités de traitement du langage naturel ne seront pas disponibles.")

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
    'HAS_SKLEARN'
]