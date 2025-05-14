#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test du mode simulation pour l'API Google Maps
"""

import os
import logging
from dotenv import load_dotenv
from app.google_maps_client import GoogleMapsClient
from app.smartmatch_transport import CommuteMatchExtension

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_simulation_mode():
    """Teste le mode simulation du client Google Maps"""
    # Chargement des variables d'environnement
    load_dotenv()
    
    logger.info("=== TEST DU MODE SIMULATION DE L'API GOOGLE MAPS ===")
    
    # Création du client en mode simulation
    client = GoogleMapsClient(use_mock_mode=True)
    logger.info("✅ Client Google Maps initialisé en mode simulation")
    
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
    
    # Test des temps de trajet individuels
    for origin in origins:
        for destination in destinations:
            for mode in ["driving", "transit", "bicycling", "walking"]:
                time = client.get_travel_time(origin, destination, mode=mode)
                logger.info(f"✅ Temps de trajet en {mode} de {origin} à {destination}: {time} minutes")
    
    # Test du geocodage
    addresses = [
        "Paris, France",
        "La Tour Eiffel, Paris",
        "10 Downing Street, London",
        "Champs-Élysées, Paris, France"
    ]
    
    for address in addresses:
        coords = client.geocode_address(address)
        if coords:
            lat, lng = coords
            logger.info(f"✅ Géocodage de '{address}': ({lat:.6f}, {lng:.6f})")
        else:
            logger.warning(f"⚠️ Échec du géocodage pour '{address}'")
    
    # Test de l'extension de transport
    logger.info("=== TEST DE L'EXTENSION DE TRANSPORT AVEC SIMULATION ===")
    
    # Création de l'extension avec le client simulé
    extension = CommuteMatchExtension(client)
    logger.info("✅ Extension de transport initialisée avec le client simulé")
    
    # Test du score de trajet
    candidate_address = "20 Rue de la Paix, 75002 Paris, France"
    job_address = "Tour Montparnasse, 75015 Paris, France"
    
    score = extension.calculate_commute_score(candidate_address, job_address)
    logger.info(f"✅ Score de trajet: {score}")
    
    # Test de l'analyse détaillée
    analysis = extension.analyze_commute_compatibility(
        candidate_address=candidate_address,
        job_address=job_address,
        candidate_preferences={
            "max_commute_minutes": 30,
            "preferred_mode": "transit",
            "accepts_remote": True
        },
        job_requirements={
            "is_remote": False,
            "is_hybrid": True,
            "days_in_office": 3
        }
    )
    
    logger.info(f"✅ Analyse détaillée: {analysis}")
    
    logger.info("=== TESTS TERMINÉS ===")
    logger.info("Pour utiliser le mode simulation dans votre code:")
    logger.info("  client = GoogleMapsClient(use_mock_mode=True)")
    logger.info("  extension = CommuteMatchExtension(client)")

if __name__ == "__main__":
    test_simulation_mode()
