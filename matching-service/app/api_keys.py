# Configuration des clés API pour les services externes
# Ce fichier doit être configuré avec des variables d'environnement

import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Google Maps API Key
# Utiliser une variable d'environnement au lieu d'une clé en dur
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')

if not GOOGLE_MAPS_API_KEY:
    print("ATTENTION: GOOGLE_MAPS_API_KEY non définie. Veuillez configurer cette variable d'environnement.")
    print("Exemple: export GOOGLE_MAPS_API_KEY='votre_cle_ici'")

# Pour d'autres clés API, suivez le même pattern :
# OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
# ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
# etc.
