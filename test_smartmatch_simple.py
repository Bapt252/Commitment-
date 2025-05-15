#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Script pour tester l'intégration de SmartMatch avec les services de parsing existants."""

import os
import sys
import logging
import argparse

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("TestIntegration")

def test_matching(cv_path, job_text):
    """Teste le matching entre un CV et une description de poste."""
    logger.info("=== Test de l'intégration SmartMatch ===")
    
    # Charger le CV
    logger.info(f"Lecture du CV depuis: {cv_path}")
    try:
        with open(cv_path, "rb") as f:
            cv_content = f.read()
        logger.info(f"CV chargé avec succès, taille: {len(cv_content)} octets")
    except Exception as e:
        logger.error(f"Erreur lors de la lecture du CV: {str(e)}")
        return
    
    # Simuler un matching simple
    logger.info("Simulation de matching CV avec description de poste")
    logger.info(f"Description du poste: {job_text[:100]}...")
    
    # Simuler un résultat de matching
    result = {
        "status": "success",
        "candidate": {"name": "Candidat de test"},
        "job": {"title": "Poste de test"},
        "score": 0.75,
        "details": {
            "skills": 0.8,
            "experience": 0.7,
            "education": 0.6,
            "location": 0.9
        }
    }
    
    logger.info("=== Résultat du matching ===")
    logger.info(f"CV: {result['candidate']['name']}")
    logger.info(f"Poste: {result['job']['title']}")
    logger.info(f"Score de matching: {result['score']}")
    logger.info("Détails du matching:")
    for category, score in result["details"].items():
        logger.info(f"  - {category}: {score}")

def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(description="Test d'intégration de SmartMatch")
    parser.add_argument("--cv", required=True, help="Chemin vers le fichier CV")
    parser.add_argument("--job", help="Texte de la description de poste")
    parser.add_argument("--job-file", help="Chemin vers le fichier de description de poste")
    
    args = parser.parse_args()
    
    # Vérifier qu'au moins une description de poste est fournie
    if not args.job and not args.job_file:
        logger.error("Vous devez fournir soit --job, soit --job-file")
        sys.exit(1)
    
    # Récupérer le texte de la description de poste
    job_text = args.job
    if args.job_file:
        try:
            with open(args.job_file, "r", encoding="utf-8") as f:
                job_text = f.read()
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du fichier de poste: {str(e)}")
            sys.exit(1)
    
    # Exécuter le test de matching
    test_matching(args.cv, job_text)

if __name__ == "__main__":
    main()
