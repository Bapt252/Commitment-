#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Module principal pour exécuter le système Nexten SmartMatch."""

import os
import sys
import json
import logging
import argparse
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SmartMatch")

# Import des modules du projet
from app.smartmatch import SmartMatchEngine
from app.compat import GoogleMapsClient
from app.semantic_analysis import SemanticAnalyzer
from app.data_loader import DataLoader
from app.insight_generator import InsightGenerator

def parse_arguments():
    """Parse les arguments de ligne de commande."""
    parser = argparse.ArgumentParser(description='Nexten SmartMatch - Système de matching bidirectionnel')
    
    parser.add_argument('--candidates', type=str, required=True,
                        help='Chemin vers le fichier de données des candidats (JSON ou CSV)')
    parser.add_argument('--companies', type=str, required=True,
                        help='Chemin vers le fichier de données des entreprises (JSON ou CSV)')
    parser.add_argument('--output', type=str, default='./results/matching_results.json',
                        help='Chemin du fichier de sortie pour les résultats (JSON ou CSV)')
    parser.add_argument('--weights', type=str, default=None,
                        help='Pondérations personnalisées au format JSON (ex: {"skills": 0.4, "location": 0.3, ...})')
    parser.add_argument('--threshold', type=float, default=0.6,
                        help='Seuil minimum pour considérer un match')
    parser.add_argument('--google-maps-key', type=str, default=None,
                        help='Clé API Google Maps pour le calcul des temps de trajet')
    parser.add_argument('--verbose', action='store_true',
                        help='Afficher des informations détaillées pendant l\'exécution')
    
    return parser.parse_args()

def main():
    """Fonction principale."""
    # Parsing des arguments
    args = parse_arguments()
    
    # Configuration du niveau de logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Affichage des informations de démarrage
    logger.info("Démarrage du système Nexten SmartMatch")
    
    # Configuration de la clé API Google Maps
    if args.google_maps_key:
        os.environ['GOOGLE_MAPS_API_KEY'] = args.google_maps_key
        logger.info("Clé API Google Maps configurée")
    else:
        logger.warning("Aucune clé API Google Maps fournie. Les temps de trajet ne seront pas calculés précisément.")
    
    try:
        # Chargement des données
        data_loader = DataLoader()
        
        logger.info(f"Chargement des données des candidats depuis {args.candidates}")
        candidates = data_loader.load_candidates(args.candidates)
        logger.info(f"{len(candidates)} candidats chargés")
        
        logger.info(f"Chargement des données des entreprises depuis {args.companies}")
        companies = data_loader.load_companies(args.companies)
        logger.info(f"{len(companies)} entreprises chargées")
        
        # Initialisation du moteur de matching
        engine = SmartMatchEngine()
        
        # Configuration des pondérations personnalisées
        if args.weights:
            try:
                weights = json.loads(args.weights)
                engine.set_weights(weights)
                logger.info(f"Pondérations personnalisées appliquées: {weights}")
            except json.JSONDecodeError as e:
                logger.error(f"Erreur lors du parsing des pondérations: {e}")
                logger.info("Utilisation des pondérations par défaut")
        
        # Configuration du seuil minimum
        engine.min_score_threshold = args.threshold
        logger.info(f"Seuil minimum de matching configuré à {args.threshold}")
        
        # Exécution du matching
        logger.info("Exécution du matching...")
        matching_results = engine.match(candidates, companies)
        logger.info(f"{len(matching_results)} matchings trouvés")
        
        # Génération d'insights
        logger.info("Génération d'insights...")
        insight_generator = InsightGenerator()
        insights = insight_generator.generate_insights(matching_results)
        logger.info(f"{len(insights)} insights générés")
        
        # Préparation des résultats finaux
        final_results = {
            "matches": matching_results,
            "insights": insights,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "candidates_count": len(candidates),
                "companies_count": len(companies),
                "matches_count": len(matching_results),
                "threshold": args.threshold,
                "weights": engine.weights
            }
        }
        
        # Sauvegarde des résultats
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(final_results, f, ensure_ascii=False, indent=2)
        logger.info(f"Résultats sauvegardés dans {args.output}")
        
        # Affichage des meilleurs matchings
        if matching_results:
            logger.info("\nTop 5 des meilleurs matchings:")
            for i, match in enumerate(matching_results[:5]):
                logger.info(f"{i+1}. Candidat {match['candidate_id']} - Entreprise {match['company_id']} - Score: {match['score']:.2f}")
        
        # Affichage des insights clés
        if insights:
            logger.info("\nInsights clés:")
            for i, insight in enumerate(insights[:3]):
                logger.info(f"{i+1}. {insight['message']}")
        
        logger.info("Traitement terminé avec succès")
        return 0
    
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())