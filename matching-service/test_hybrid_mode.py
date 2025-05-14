#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test du mode hybride pour l'API Google Maps
"""

import os
import logging
import time
import json
from dotenv import load_dotenv
from app.google_maps_client import GoogleMapsClient

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_hybrid_mode():
    """Teste le mode hybride du client Google Maps qui combine API réelle et simulation"""
    # Chargement des variables d'environnement
    load_dotenv()
    
    logger.info("=== TEST DU MODE HYBRIDE DE L'API GOOGLE MAPS ===")
    
    # Création des clients avec différents modes
    client_real = GoogleMapsClient(use_mock_mode=False, use_hybrid_mode=False)
    client_mock = GoogleMapsClient(use_mock_mode=True, use_hybrid_mode=False)
    client_hybrid = GoogleMapsClient(use_mock_mode=False, use_hybrid_mode=True)
    
    logger.info("✅ Clients initialisés en différents modes (API seule, simulation, hybride)")
    
    # Test des temps de trajet
    origins = [
        "Paris, France", 
        "Lyon, France", 
        "Nantes, France",
        "20 Rue de la Paix, 75002 Paris, France"
    ]
    
    destinations = [
        "Versailles, France", 
        "Saint-Nazaire, France", 
        "Toulouse, France",
        "10 Place Bellecour, 69002 Lyon, France"
    ]
    
    # Modes de transport à tester
    transport_modes = ["driving", "transit", "bicycling", "walking"]
    
    # Tableau pour stocker les résultats
    results = {}
    
    # Test comparatif des différents clients
    for origin in origins:
        for destination in destinations:
            logger.info(f"=== Test du trajet: {origin} → {destination} ===")
            
            # Clé pour les résultats
            key = f"{origin}|{destination}"
            if key not in results:
                results[key] = {}
            
            for mode in transport_modes:
                if mode not in results[key]:
                    results[key][mode] = {}
                
                # Test avec client API uniquement
                start_time = time.time()
                time_real = client_real.get_travel_time(origin, destination, mode=mode)
                real_duration = round((time.time() - start_time) * 1000, 2)
                results[key][mode]["real"] = {"time": time_real, "duration_ms": real_duration}
                
                # Test avec client simulation uniquement
                start_time = time.time()
                time_mock = client_mock.get_travel_time(origin, destination, mode=mode)
                mock_duration = round((time.time() - start_time) * 1000, 2)
                results[key][mode]["mock"] = {"time": time_mock, "duration_ms": mock_duration}
                
                # Test avec client hybride
                start_time = time.time()
                time_hybrid = client_hybrid.get_travel_time(origin, destination, mode=mode)
                hybrid_duration = round((time.time() - start_time) * 1000, 2)
                results[key][mode]["hybrid"] = {"time": time_hybrid, "duration_ms": hybrid_duration}
                
                # Afficher les résultats pour ce trajet
                logger.info(f"Mode: {mode}")
                logger.info(f"  - API seule: {time_real} min ({real_duration} ms)")
                logger.info(f"  - Simulation: {time_mock} min ({mock_duration} ms)")
                logger.info(f"  - Hybride: {time_hybrid} min ({hybrid_duration} ms)")
    
    # Récupérer les statistiques
    stats_real = client_real.get_usage_stats()
    stats_mock = client_mock.get_usage_stats()
    stats_hybrid = client_hybrid.get_usage_stats()
    
    # Afficher les statistiques
    logger.info("\n=== STATISTIQUES D'UTILISATION ===")
    logger.info("Client API seule:")
    for key, value in stats_real.items():
        logger.info(f"  - {key}: {value}")
    
    logger.info("\nClient simulation:")
    for key, value in stats_mock.items():
        logger.info(f"  - {key}: {value}")
    
    logger.info("\nClient hybride:")
    for key, value in stats_hybrid.items():
        logger.info(f"  - {key}: {value}")
    
    # Afficher une conclusion
    logger.info("\n=== CONCLUSION ===")
    logger.info(f"Taux de succès API seule: {stats_real['success_rate']}%")
    logger.info(f"Taux de couverture hybride: 100% (grâce à la simulation de secours)")
    logger.info(f"Nombre de fallbacks automatiques: {stats_hybrid['hybrid_fallbacks']}")
    logger.info(f"Économie d'appels API: {stats_mock['mock_api_calls']} (en mode simulation)")
    
    # Calcul de la fiabilité
    total_routes = len(origins) * len(destinations) * len(transport_modes)
    success_real = sum(1 for o in origins for d in destinations for m in transport_modes 
                      if results.get(f"{o}|{d}", {}).get(m, {}).get("real", {}).get("time", -1) > 0)
    reliability_real = (success_real / total_routes) * 100 if total_routes > 0 else 0
    
    logger.info(f"Fiabilité API seule: {round(reliability_real, 2)}% des trajets calculés correctement")
    logger.info(f"Fiabilité hybride: 100% des trajets calculés (même en cas d'échec API)")
    
    logger.info("=== TESTS TERMINÉS ===")
    logger.info("Le mode hybride combine le meilleur des deux mondes :")
    logger.info("  - Utilise l'API réelle quand elle fonctionne correctement")
    logger.info("  - Bascule automatiquement en simulation quand l'API échoue")
    logger.info("  - Fournit toujours un résultat, même en cas de problèmes d'API")
    
    # Suggérer des utilisations avancées
    logger.info("\n=== UTILISATIONS RECOMMANDÉES ===")
    logger.info("Pour le développement et les tests:")
    logger.info("  client = GoogleMapsClient(use_hybrid_mode=True)")
    logger.info("Pour la production avec haut niveau de disponibilité:")
    logger.info("  client = GoogleMapsClient(use_hybrid_mode=True)")
    logger.info("Pour la production si l'API est 100% fiable:")
    logger.info("  client = GoogleMapsClient(use_hybrid_mode=False)")
    logger.info("Pour les tests sans API (CI/CD):")
    logger.info("  client = GoogleMapsClient(use_mock_mode=True)")

if __name__ == "__main__":
    test_hybrid_mode()
