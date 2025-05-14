#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test simple du client hybride avec l'extension de transport
"""

import os
import logging
from dotenv import load_dotenv
from app.hybrid_maps_client import HybridGoogleMapsClient
from app.smartmatch_transport import CommuteMatchExtension

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_simple():
    """Test simple pour vérifier le fonctionnement du client hybride avec l'extension de transport"""
    
    # Charger la clé API Google Maps
    load_dotenv()
    
    logger.info("=== TEST SIMPLE DU CLIENT HYBRIDE AVEC L'EXTENSION DE TRANSPORT ===")
    
    # Initialiser le client hybride
    maps_client = HybridGoogleMapsClient()
    logger.info("✅ Client hybride initialisé")
    
    # Tester un temps de trajet
    origin = "Paris, France"
    destination = "Lyon, France"
    mode = "driving"
    
    time = maps_client.get_travel_time(origin, destination, mode)
    logger.info(f"✅ Temps de trajet {origin} → {destination} en {mode}: {time} minutes")
    
    # Initialiser l'extension de transport
    transport_extension = CommuteMatchExtension(maps_client)
    logger.info("✅ Extension de transport initialisée avec le client hybride")
    
    # Tester le calcul du score de trajet
    candidate_address = "20 Rue de la Paix, 75002 Paris, France"
    job_address = "Tour Montparnasse, 75015 Paris, France"
    
    score = transport_extension.calculate_commute_score(
        candidate_address=candidate_address,
        job_address=job_address,
        is_remote=False,
        is_hybrid=True
    )
    
    logger.info(f"✅ Score de trajet: {score}")
    
    # Tester l'analyse de compatibilité
    analysis = transport_extension.analyze_commute_compatibility(
        candidate_address=candidate_address,
        job_address=job_address,
        candidate_preferences={
            "max_commute_minutes": 45,
            "preferred_mode": "transit",
            "accepts_remote": True
        },
        job_requirements={
            "is_remote": False,
            "is_hybrid": True,
            "days_in_office": 3
        }
    )
    
    logger.info(f"✅ Analyse de compatibilité: {analysis}")
    
    # Afficher les statistiques
    if hasattr(maps_client, 'stats'):
        logger.info("\nStatistiques d'utilisation:")
        for key, value in maps_client.stats.items():
            logger.info(f"  - {key}: {value}")
    
    logger.info("=== TEST TERMINÉ ===")
    logger.info("Tout fonctionne correctement ! Le client hybride est compatible avec l'extension de transport.")

if __name__ == "__main__":
    test_simple()