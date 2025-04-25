#!/usr/bin/env python
"""
Script de préchargement des modèles NLP pour éviter les téléchargements lazys 
qui peuvent échouer dans les conteneurs Docker.

Ce script est exécuté au démarrage des services pour s'assurer que tous les modèles
nécessaires sont correctement téléchargés et disponibles.
"""
import os
import sys
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('preload_models')

def preload_sentence_transformers():
    """Précharge les modèles sentence-transformers"""
    try:
        from sentence_transformers import SentenceTransformer
        
        # Modèle pour les embeddings multilingues
        logger.info("Chargement du modèle sentence-transformers multilingue...")
        model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
        # Test d'encodage basique pour vérifier le bon fonctionnement
        test_embedding = model.encode("Ceci est un test de préchargement du modèle")
        logger.info(f"Modèle chargé avec succès, taille d'embedding: {len(test_embedding)}")
        
        # Vérifier le répertoire des modèles
        import torch
        cache_dir = os.path.join(os.path.expanduser('~'), '.cache', 'torch', 'sentence_transformers')
        if os.path.exists(cache_dir):
            logger.info(f"Modèles stockés dans: {cache_dir}")
            
        return True
    except Exception as e:
        logger.error(f"Erreur lors du chargement du modèle sentence-transformers: {e}")
        return False

# Importer et appliquer le module de compatibilité OpenAI
def check_openai_compatibility():
    """Vérifie que le module de compatibilité OpenAI fonctionne correctement"""
    try:
        # Import explicite pour appliquer le patch
        import compat
        
        # Vérifier l'importation d'OpenAI
        import openai
        
        # Vérifier la version
        logger.info(f"Version d'OpenAI: {openai.__version__}")
        if openai.__version__ != "0.28.1":
            logger.warning(f"Version d'OpenAI inattendue: {openai.__version__}, 0.28.1 attendue")
        
        # Vérifier la présence de la classe ChatCompletion
        if hasattr(openai, 'ChatCompletion'):
            logger.info("Classe ChatCompletion présente dans OpenAI")
            return True
        else:
            logger.error("Le patch de compatibilité n'a pas fonctionné, ChatCompletion n'est pas disponible")
            return False
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de la compatibilité OpenAI: {e}")
        return False

if __name__ == "__main__":
    logger.info("Démarrage du préchargement des modèles...")
    
    # Exécuter tous les préchargements
    results = [
        ("Sentence Transformers", preload_sentence_transformers()),
        ("OpenAI Compatibility", check_openai_compatibility())
    ]
    
    # Afficher un résumé
    logger.info("=== Résumé du préchargement ===")
    all_success = True
    for name, success in results:
        status = "✅ OK" if success else "❌ ÉCHEC"
        logger.info(f"{name}: {status}")
        all_success = all_success and success
    
    if all_success:
        logger.info("✅ Tous les modèles ont été préchargés avec succès!")
        sys.exit(0)
    else:
        logger.error("❌ Certains modèles n'ont pas pu être préchargés.")
        sys.exit(1)
