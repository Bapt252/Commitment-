#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Script pour tester l'intégration de SmartMatch avec les services de parsing existants."""

import os
import sys
import logging
import asyncio
import argparse
from dotenv import load_dotenv

# Ajouter le répertoire racine au chemin d'exécution
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.factories import ServiceFactory
from app.adapters.matching_pipeline import MatchingPipeline

# Charger les variables d'environnement depuis le fichier .env s'il existe
load_dotenv()

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("TestIntegration")

async def test_matching(cv_path: str, job_text: str):
    """
    Teste le matching entre un CV et une description de poste.
    
    Args:
        cv_path: Chemin vers le fichier CV
        job_text: Texte de la description de poste
    """
    logger.info("=== Test de l'intégration SmartMatch avec les services de parsing existants ===")
    
    # Créer le service de parsing
    cv_parser_url = os.environ.get("CV_PARSER_URL", "http://localhost:5051")
    job_parser_url = os.environ.get("JOB_PARSER_URL", "http://localhost:5055")
    parser_service_type = os.environ.get("DEFAULT_PARSER_SERVICE", "combined")
    
    logger.info(f"Utilisation du service de parsing: {parser_service_type}")
    logger.info(f"URL du service de parsing CV: {cv_parser_url}")
    logger.info(f"URL du service de parsing de fiches de poste: {job_parser_url}")
    
    try:
        parser_service = ServiceFactory.create_parser_service(
            service_type=parser_service_type,
            cv_parser_url=cv_parser_url,
            job_parser_url=job_parser_url
        )
        
        # Créer l'adaptateur de parsing
        parsing_adapter = ServiceFactory.create_parsing_adapter(parser_service)
        
        # Créer le pipeline de matching
        pipeline = MatchingPipeline(parsing_adapter)
        
        logger.info(f"Lecture du CV depuis: {cv_path}")
        with open(cv_path, "rb") as f:
            cv_content = f.read()
        
        logger.info("Matching CV avec description de poste...")
        result = await pipeline.match_cv_to_job(cv_content, os.path.basename(cv_path), job_text)
        
        if result.get("status") == "success":
            logger.info("=== Résultat du matching ===")
            logger.info(f"CV: {result['candidate']['name']}")
            logger.info(f"Poste: {result['job']['title']}")
            logger.info(f"Score de matching: {result['score']}")
            logger.info("Détails du matching:")
            for category, score in result["details"].items():
                logger.info(f"  - {category}: {score}")
        else:
            logger.error(f"Erreur lors du matching: {result.get('message', 'Erreur inconnue')}")
    
    except Exception as e:
        logger.exception(f"Exception lors du test: {str(e)}")

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
        with open(args.job_file, "r", encoding="utf-8") as f:
            job_text = f.read()
    
    # Exécuter le test de matching
    asyncio.run(test_matching(args.cv, job_text))

if __name__ == "__main__":
    main()
