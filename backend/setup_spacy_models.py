#!/usr/bin/env python3
"""
Script d'installation des modèles spaCy.
Télécharge automatiquement les modèles si non présents.
"""

import spacy
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_spacy_models():
    """Télécharge les modèles spaCy nécessaires si non installés."""
    models = {
        'fr_core_news_md': 'French medium model',
        'en_core_web_sm': 'English small model'
    }
    
    for model_name, description in models.items():
        try:
            spacy.load(model_name)
            logger.info(f"✅ {description} ({model_name}) already installed")
        except OSError:
            logger.info(f"📦 Downloading {description} ({model_name})...")
            try:
                spacy.cli.download(model_name)
                # Vérifier que le modèle est bien installé
                spacy.load(model_name)
                logger.info(f"✅ {description} ({model_name}) successfully installed")
            except Exception as e:
                logger.error(f"❌ Failed to install {model_name}: {e}")
                sys.exit(1)

if __name__ == "__main__":
    setup_spacy_models()