"""
Script de pré-chargement des modèles pour le service de parsing de fiches de poste.
Permet de charger les modèles nécessaires au démarrage du service pour éviter
des temps de chargement lors des premières requêtes.
"""

import os
import logging
import importlib.util
import sys
import time

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

def preload_models():
    """Charge les modèles et dépendances nécessaires au démarrage"""
    start_time = time.time()
    logger.info("Démarrage du pré-chargement des modèles et dépendances...")
    
    models_loaded = []
    
    # Liste des bibliothèques à précharger
    libraries_to_preload = [
        "openai",
        "pydantic",
        "PyPDF2",
        "docx",
        "pdfminer",
    ]
    
    # Préchargement des bibliothèques standard
    for lib_name in libraries_to_preload:
        try:
            if importlib.util.find_spec(lib_name):
                importlib.import_module(lib_name)
                models_loaded.append(lib_name)
                logger.info(f"Bibliothèque {lib_name} préchargée avec succès")
            else:
                logger.warning(f"Bibliothèque {lib_name} non disponible, ignorée")
        except ImportError as e:
            logger.warning(f"Erreur lors du chargement de {lib_name}: {str(e)}")
    
    # Tentative de préchargement des bibliothèques optionnelles
    optional_libraries = [
        "textract",  # Pour l'extraction de texte avancée
        "pdfplumber",  # Alternative pour PDF
        "pytesseract",  # Pour OCR
        "pdf2image",  # Pour conversion PDF->Image (OCR)
        "striprtf",  # Pour fichiers RTF
    ]
    
    for lib_name in optional_libraries:
        try:
            if importlib.util.find_spec(lib_name):
                importlib.import_module(lib_name)
                models_loaded.append(f"{lib_name} (optionnel)")
                logger.info(f"Bibliothèque optionnelle {lib_name} préchargée avec succès")
        except ImportError:
            logger.info(f"Bibliothèque optionnelle {lib_name} non disponible")
    
    # Vérification de la clé API OpenAI
    if os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENAI"):
        logger.info("Clé API OpenAI détectée")
        models_loaded.append("OpenAI API")
    else:
        logger.warning("Aucune clé API OpenAI détectée - le service fonctionnera en mode mock")
    
    elapsed_time = time.time() - start_time
    logger.info(f"Pré-chargement terminé en {elapsed_time:.2f} secondes")
    logger.info(f"Éléments chargés: {', '.join(models_loaded)}")

if __name__ == "__main__":
    preload_models()
