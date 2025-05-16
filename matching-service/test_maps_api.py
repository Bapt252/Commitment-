#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour l'API Google Maps dans le système Nexten SmartMatch
"""

import os
import logging
import json
import time
from dotenv import load_dotenv
from app.google_maps_client import GoogleMapsClient
from app.maps_cache import MapsCache

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_api():
    """Teste les différentes fonctionnalités de l'API Google Maps"""
    # Chargement des variables d'environnement
    load_dotenv()
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    
    logger.info("=== TEST DE L'API GOOGLE MAPS ===")
    
    if not api_key:
        logger.warning("⚠️ Clé API Google Maps non trouvée dans .env")
        logger.info("➡️ Le test se poursuit en mode hybride/simulation")
    else:
        logger.info(f"✅ Clé API Google Maps chargée: {api_key[:5]}...{api_key[-5:] if len(api_key) > 10 else '***'}")
    
    # Initialisation du client
    try:
        client = GoogleMapsClient(api_key=api_key, use_hybrid_mode=True)
        logger.info("✅ Client initialisé avec succès")
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation du client: {e}")
        return False
    
    # Tester le cache
    logger.info("=== TEST DU CACHE ===")
    cache = MapsCache()
    
    # Mettre une valeur en cache
    cache.set("test", "success", param="value")
    
    # Récupérer la valeur
    cached_value = cache.get("test", param="value")
    if cached_value == "success":
        logger.info("✅ Test du cache réussi")
    else:
        logger.error("❌ Échec du test du cache")
    
    # Test de base: Paris-Lyon
    try:
        logger.info("=== TEST DE TRAJET DE BASE ===")
        
        # Premier appel (devrait utiliser l'API si disponible)
        start_time = time.time()
        result = client.get_travel_time("Paris, France", "Lyon, France", mode="driving")
        duration = time.time() - start_time
        logger.info(f"✅ Temps de trajet en voiture Paris-Lyon: {result} minutes (obtenu en {duration:.2f}s)")
        
        # Deuxième appel (devrait utiliser le cache)
        start_time = time.time()
        result2 = client.get_travel_time("Paris, France", "Lyon, France", mode="driving")
        duration2 = time.time() - start_time
        logger.info(f"✅ Deuxième appel (cache): {result2} minutes (obtenu en {duration2:.2f}s)")
        
        # Vérifier l'accélération
        if duration2 < duration:
            logger.info(f"✅ Cache efficace: {duration/duration2:.1f}x plus rapide")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du calcul Paris-Lyon: {e}")
    
    # Test avec différents modes de transport pour une distance plus courte
    locations = [
        ("Paris, France", "Versailles, France"),
        ("Nantes, France", "Saint-Nazaire, France"),
        ("75001, France", "92100, France")
    ]
    
    logger.info("=== TEST DES DIFFÉRENTS MODES DE TRANSPORT ===")
    for origin, destination in locations:
        logger.info(f"Test de trajet: {origin} → {destination}")
        modes = ["driving", "transit", "bicycling", "walking"]
        for mode in modes:
            try:
                time_result = client.get_travel_time(origin, destination, mode=mode)
                logger.info(f"✅ Temps de trajet en {mode}: {time_result} minutes")
            except Exception as e:
                logger.error(f"❌ Erreur pour le mode {mode}: {e}")
    
    # Test de géocodage d'adresses
    logger.info("=== TEST DE GÉOCODAGE ===")
    test_addresses = [
        "Tour Eiffel, Paris, France",
        "10 Downing Street, London, UK",
        "1600 Pennsylvania Avenue, Washington DC, USA"
    ]
    
    for address in test_addresses:
        try:
            coords = client.geocode_address(address)
            if coords:
                lat, lng = coords
                logger.info(f"✅ Géocodage de '{address}': {lat:.4f}, {lng:.4f}")
            else:
                logger.warning(f"⚠️ Impossible de géocoder '{address}'")
        except Exception as e:
            logger.error(f"❌ Erreur lors du géocodage de '{address}': {e}")
    
    # Test de matrice de distance
    logger.info("=== TEST DE MATRICE DE DISTANCE ===")
    origins = ["Paris, France", "Lyon, France"]
    destinations = ["Marseille, France", "Bordeaux, France"]
    
    try:
        matrix = client.get_distance_matrix(origins, destinations)
        logger.info(f"✅ Matrice de distance obtenue pour {len(origins)} origines et {len(destinations)} destinations")
        
        # Afficher quelques résultats
        if "rows" in matrix:
            for i, origin in enumerate(origins):
                for j, destination in enumerate(destinations):
                    element = matrix["rows"][i]["elements"][j]
                    if element.get("status") == "OK":
                        distance = element.get("distance", {}).get("text", "N/A")
                        duration = element.get("duration", {}).get("text", "N/A")
                        logger.info(f"{origin} → {destination}: {distance} ({duration})")
    except Exception as e:
        logger.error(f"❌ Erreur lors du calcul de la matrice de distance: {e}")
    
    # Test d'adresses spécifiques d'entreprises/candidats
    logger.info("=== TEST D'ADRESSES DU SYSTÈME DE MATCHING ===")
    try:
        from test.data import sample_addresses
        for address in sample_addresses.SAMPLE_ADDRESSES[:3]:  # Limiter à 3 pour le test
            logger.info(f"Vérification de l'adresse: {address}")
            geocode = client.geocode_address(address)
            if geocode:
                logger.info(f"✅ Adresse valide: {geocode}")
            else:
                logger.warning(f"⚠️ Impossible de géocoder: {address}")
    except ImportError:
        logger.warning("⚠️ Module d'adresses d'exemple non trouvé, test ignoré")
    
    # Afficher les statistiques
    logger.info("=== STATISTIQUES D'UTILISATION ===")
    stats = client.get_usage_stats()
    
    # Afficher les statistiques principales
    for key in ["total_calls", "real_api_calls", "mock_api_calls", "cached_results", 
                "success_rate", "hybrid_fallbacks", "mode"]:
        if key in stats:
            logger.info(f"{key}: {stats[key]}")
    
    # Afficher les statistiques du cache
    if "cache" in stats:
        logger.info("Statistiques du cache:")
        for key, value in stats["cache"].items():
            logger.info(f"  {key}: {value}")
    
    logger.info("=== TESTS TERMINÉS ===")
    return True

if __name__ == "__main__":
    test_api()
