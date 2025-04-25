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

def preload_spacy_models():
    """Précharge les modèles spaCy"""
    try:
        import spacy
        
        # Modèles français et anglais
        logger.info("Chargement des modèles spaCy...")
        fr_model = spacy.load("fr_core_news_md")
        en_model = spacy.load("en_core_web_sm")
        
        # Test rapide
        fr_doc = fr_model("Ceci est un test en français.")
        en_doc = en_model("This is a test in English.")
        
        logger.info(f"Modèles spaCy chargés avec succès: {fr_model.meta['name']} et {en_model.meta['name']}")
        return True
    except Exception as e:
        logger.error(f"Erreur lors du chargement des modèles spaCy: {e}")
        return False

def preload_nltk_data():
    """Précharge les données NLTK nécessaires"""
    try:
        import nltk
        
        # Télécharger les ressources NLTK couramment utilisées
        logger.info("Téléchargement des données NLTK...")
        nltk_packages = ['punkt', 'stopwords', 'wordnet']
        for package in nltk_packages:
            try:
                nltk.data.find(f'tokenizers/{package}')
                logger.info(f"Package NLTK '{package}' déjà téléchargé")
            except LookupError:
                logger.info(f"Téléchargement du package NLTK '{package}'...")
                nltk.download(package, quiet=True)
        
        return True
    except Exception as e:
        logger.error(f"Erreur lors du téléchargement des données NLTK: {e}")
        return False

if __name__ == "__main__":
    logger.info("Démarrage du préchargement des modèles...")
    
    # Exécuter tous les préchargements
    results = [
        ("Sentence Transformers", preload_sentence_transformers()),
        ("SpaCy", preload_spacy_models()),
        ("NLTK", preload_nltk_data())
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
