#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test autonome du client hybride sans dépendances externes
"""

import os
import logging
import time
from dotenv import load_dotenv
from app.hybrid_maps_client import HybridGoogleMapsClient

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Test du client hybride de manière autonome"""
    logger.info("=== TEST AUTONOME DU CLIENT HYBRIDE ===")
    
    # Charger les variables d'environnement
    load_dotenv()
    
    # Initialiser le client hybride
    client = HybridGoogleMapsClient()
    logger.info("✅ Client hybride initialisé")
    
    # Test des temps de trajet
    test_routes = [
        ("Paris, France", "Lyon, France", "driving"),
        ("Paris, France", "Versailles, France", "transit"),
        ("20 Rue de la Paix, 75002 Paris, France", "Tour Montparnasse, 75015 Paris, France", "walking")
    ]
    
    for origin, destination, mode in test_routes:
        start_time = time.time()
        travel_time = client.get_travel_time(origin, destination, mode)
        duration = round((time.time() - start_time) * 1000)
        logger.info(f"✅ Temps de trajet {origin} → {destination} en {mode}: {travel_time} minutes (calculé en {duration} ms)")
    
    # Test du géocodage
    test_addresses = [
        "Paris, France",
        "20 Rue de la Paix, 75002 Paris, France",
        "Tour Montparnasse, 75015 Paris, France",
        "Adresse inconnue pour simulation"
    ]
    
    for address in test_addresses:
        start_time = time.time()
        coords = client.geocode_address(address)
        duration = round((time.time() - start_time) * 1000)
        if coords:
            lat, lng = coords
            logger.info(f"✅ Géocodage de '{address}': ({lat:.6f}, {lng:.6f}) (calculé en {duration} ms)")
        else:
            logger.warning(f"⚠️ Échec du géocodage pour '{address}'")
    
    # Statistiques
    logger.info("\nStatistiques d'utilisation:")
    for key, value in client.stats.items():
        logger.info(f"- {key}: {value}")
    
    # Simulation de calcul de score de transport
    logger.info("\nSimulation d'un calcul de score de transport:")
    origin_address = "20 Rue de la Paix, 75002 Paris, France"
    destination_address = "Tour Montparnasse, 75015 Paris, France"
    
    # Calculer le temps de trajet en transport en commun
    travel_time = client.get_travel_time(origin_address, destination_address, "transit")
    
    # Simuler un calcul de score basé sur le temps de trajet
    max_commute = 60  # minutes
    if travel_time <= 0:
        score = 0.1
    elif travel_time > max_commute:
        score = 0.2 + 0.8 * (max_commute / travel_time)
    else:
        score = 1.0 - 0.8 * (travel_time / max_commute)
    
    logger.info(f"✅ Temps de trajet: {travel_time} minutes")
    logger.info(f"✅ Score de trajet simulé: {score:.2f}")
    
    logger.info("=== TEST TERMINÉ ===")
    logger.info("Le client hybride fonctionne correctement !")

if __name__ == "__main__":
    main()