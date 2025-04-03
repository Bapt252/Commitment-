#!/usr/bin/env python
"""
Script pour installer les dépendances NLP nécessaires.
Utilisé pour s'assurer que tous les modèles requis sont disponibles.
"""

import subprocess
import sys
import os
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("setup_nlp")

def install_spacy_models():
    """Installe ou met à jour les modèles spaCy nécessaires."""
    logger.info("Vérification des modèles spaCy...")
    
    # Modèles requis
    models = ["fr_core_news_lg"]
    
    for model in models:
        try:
            # Essayer d'importer le modèle
            __import__(model)
            logger.info(f"Modèle {model} déjà installé.")
        except ImportError:
            logger.info(f"Installation du modèle {model}...")
            subprocess.check_call([sys.executable, "-m", "spacy", "download", model])
            logger.info(f"Modèle {model} installé avec succès.")

def create_data_directories():
    """Crée les répertoires de données nécessaires s'ils n'existent pas."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    directories = ["data", "logs", "models"]
    
    for directory in directories:
        dir_path = os.path.join(base_dir, directory)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            logger.info(f"Répertoire créé: {dir_path}")
        else:
            logger.info(f"Répertoire existant: {dir_path}")

if __name__ == "__main__":
    logger.info("Début de la configuration NLP...")
    install_spacy_models()
    create_data_directories()
    logger.info("Configuration NLP terminée.")
