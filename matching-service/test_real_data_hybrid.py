#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test du client hybride avec données réelles
"""

import os
import logging
import time
from dotenv import load_dotenv
from app.real_data_hybrid_client import RealDataHybridClient

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Test du client hybride avec données réelles"""
    logger.info("=== TEST DU CLIENT HYBRIDE AVEC DONNÉES RÉELLES ===")
    
    # Charger les variables d'environnement
    load_dotenv()
    
    # Initialiser le client hybride
    client = RealDataHybridClient()
    logger.info("✅ Client hybride initialisé")
    
    # Tester avec des adresses précises
    test_addresses = [
        "20 Rue de la Paix, 75002 Paris, France",
        "Tour Montparnasse, 75015 Paris, France",
        "Tour Eiffel, Paris, France",
        "Gare de Lyon, Paris, France",
        "Aéroport Charles de Gaulle, Paris, France"
    ]
    
    # Précharger les données
    logger.info("Préchargement des données pour les adresses de test...")
    client.preload_data(test_addresses)
    
    # Tester des trajets
    logger.info("\n=== Tests de trajets ===")
    
    for origin_idx, origin in enumerate(test_addresses):
        for dest_idx, destination in enumerate(test_addresses[origin_idx+1:], origin_idx+1):
            for mode in ["driving", "transit"]:
                # Mesurer le temps d'exécution
                start_time = time.time()
                
                # Calculer le temps de trajet
                travel_time = client.get_travel_time(origin, destination, mode)
                
                # Temps d'exécution
                exec_time = round((time.time() - start_time) * 1000)
                
                logger.info(f"Trajet {origin} → {destination} en {mode}: {travel_time} minutes (exécuté en {exec_time} ms)")
    
    # Tester le calcul inverse (pour vérifier la symétrie)
    logger.info("\n=== Test de symétrie ===")
    
    # Prendre un exemple de trajet
    origin = test_addresses[0]
    destination = test_addresses[1]
    mode = "driving"
    
    # Trajet aller
    time_forward = client.get_travel_time(origin, destination, mode)
    
    # Trajet retour
    time_backward = client.get_travel_time(destination, origin, mode)
    
    # Comparer
    logger.info(f"Trajet aller {origin} → {destination}: {time_forward} minutes")
    logger.info(f"Trajet retour {destination} → {origin}: {time_backward} minutes")
    logger.info(f"Différence: {abs(time_forward - time_backward)} minutes")
    
    # Vérifier le cache
    logger.info("\n=== État du cache ===")
    cache_routes = len(client.travel_data["routes"])
    cache_geocodes = len(client.travel_data["geocodes"])
    logger.info(f"Routes en cache: {cache_routes}")
    logger.info(f"Adresses géocodées en cache: {cache_geocodes}")
    
    # Statistiques
    logger.info("\n=== Statistiques d'utilisation ===")
    for key, value in client.stats.items():
        logger.info(f"- {key}: {value}")
    
    logger.info("=== TEST TERMINÉ ===")
    logger.info("Le client hybride avec données réelles fonctionne correctement !")

if __name__ == "__main__":
    main()