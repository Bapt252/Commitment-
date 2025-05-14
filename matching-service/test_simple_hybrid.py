#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test simple du client hybride
"""

import logging
from app.hybrid_maps_client import HybridGoogleMapsClient
from app.smartmatch_transport import CommuteMatchExtension

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Test du client hybride avec l'extension transport"""
    logger.info("=== TEST SIMPLE DU CLIENT HYBRIDE ===")
    
    # Initialiser le client hybride
    client = HybridGoogleMapsClient()
    logger.info("✅ Client hybride initialisé")
    
    # Test de base
    origin = "Paris, France"
    destination = "Lyon, France"
    time = client.get_travel_time(origin, destination, "driving")
    logger.info(f"✅ Temps de trajet {origin} → {destination}: {time} minutes")
    
    # Test avec l'extension
    try:
        extension = CommuteMatchExtension(client)
        logger.info("✅ Extension transport initialisée avec le client hybride")
        
        # Calculer un score de trajet
        score = extension.calculate_commute_score(
            candidate_address="20 Rue de la Paix, 75002 Paris, France",
            job_address="Tour Montparnasse, 75015 Paris, France"
        )
        logger.info(f"✅ Score de trajet: {score}")
        logger.info("Test réussi !")
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
    
    # Statistiques
    logger.info("\nStatistiques:")
    logger.info(f"- Appels API: {client.stats['api_calls']}")
    logger.info(f"- Appels simulation: {client.stats['mock_calls']}")

if __name__ == "__main__":
    main()