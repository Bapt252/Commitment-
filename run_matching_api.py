#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Script pour démarrer l'API du service de matching SmartMatch."""

import os
import argparse
import logging
import uvicorn
from dotenv import load_dotenv
from app.adapters.matching_api import create_app
from app.factories import ServiceFactory

# Charger les variables d'environnement depuis le fichier .env s'il existe
load_dotenv()

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MatchingAPI")

def main():
    """Fonction principale pour démarrer l'API."""
    parser = argparse.ArgumentParser(description="Démarrer l'API du service de matching SmartMatch")
    parser.add_argument("--host", default="0.0.0.0", help="Adresse d'hôte (défaut: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=5052, help="Port d'écoute (défaut: 5052)")
    parser.add_argument("--debug", action="store_true", help="Activer le mode debug")
    parser.add_argument("--cv-parser-url", default=os.environ.get("CV_PARSER_URL", "http://localhost:5051"), 
                        help="URL du service de parsing de CV (défaut: http://localhost:5051)")
    parser.add_argument("--job-parser-url", default=os.environ.get("JOB_PARSER_URL", "http://localhost:5055"), 
                        help="URL du service de parsing de fiches de poste (défaut: http://localhost:5055)")
    parser.add_argument("--results-dir", default=os.environ.get("MATCHING_RESULTS_DIR", "matching_results"), 
                        help="Répertoire pour stocker les résultats (défaut: matching_results)")
    parser.add_argument("--parser-service", default=os.environ.get("DEFAULT_PARSER_SERVICE", "combined"),
                       help="Type de service de parsing à utiliser (combined, cv, job) (défaut: combined)")
    
    args = parser.parse_args()
    
    # Configurer les variables d'environnement
    os.environ["CV_PARSER_URL"] = args.cv_parser_url
    os.environ["JOB_PARSER_URL"] = args.job_parser_url
    os.environ["MATCHING_RESULTS_DIR"] = args.results_dir
    os.environ["DEFAULT_PARSER_SERVICE"] = args.parser_service
    
    logger.info(f"Démarrage de l'API SmartMatch sur {args.host}:{args.port}")
    logger.info(f"Service de parsing de CV: {args.cv_parser_url}")
    logger.info(f"Service de parsing de fiches de poste: {args.job_parser_url}")
    logger.info(f"Répertoire des résultats: {args.results_dir}")
    logger.info(f"Type de service de parsing: {args.parser_service}")
    
    # Créer le service de parsing
    parser_service = ServiceFactory.create_parser_service(
        args.parser_service, args.cv_parser_url, args.job_parser_url
    )
    
    # Créer l'adaptateur de parsing
    parsing_adapter = ServiceFactory.create_parsing_adapter(parser_service)
    
    # Créer l'application FastAPI
    app = create_app(parsing_adapter, args.results_dir)
    
    # Démarrer le serveur
    uvicorn.run(app, host=args.host, port=args.port, log_level="info" if not args.debug else "debug")

if __name__ == "__main__":
    main()
