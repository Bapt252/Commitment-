#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour l'API Google Maps dans le système Nexten SmartMatch
"""

import os
import logging
from dotenv import load_dotenv
from app.google_maps_client import GoogleMapsClient

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
    
    if not api_key:
        logger.error("❌ Clé API Google Maps non trouvée dans .env")
        return False
        
    logger.info(f"✅ Clé API Google Maps chargée: {api_key[:5]}...{api_key[-5:]}")
    
    # Initialisation du client
    try:
        client = GoogleMapsClient()
        logger.info("✅ Client initialisé avec succès")
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation du client: {e}")
        return False
    
    # Test de base: Paris-Lyon
    try:
        result = client.get_travel_time("Paris, France", "Lyon, France", mode="driving")
        logger.info(f"✅ Temps de trajet en voiture Paris-Lyon: {result} minutes")
    except Exception as e:
        logger.error(f"❌ Erreur lors du calcul Paris-Lyon: {e}")
    
    # Test avec différents modes de transport pour une distance plus courte
    locations = [
        ("Paris, France", "Versailles, France"),
        ("Nantes, France", "Saint-Nazaire, France"),
        ("75001, France", "92100, France")
    ]
    
    for origin, destination in locations:
        logger.info(f"=== Test de trajet: {origin} → {destination} ===")
        modes = ["driving", "transit", "bicycling", "walking"]
        for mode in modes:
            try:
                time = client.get_travel_time(origin, destination, mode=mode)
                logger.info(f"✅ Temps de trajet en {mode}: {time} minutes")
            except Exception as e:
                logger.error(f"❌ Erreur pour le mode {mode}: {e}")
    
    # Test d'adresses spécifiques d'entreprises/candidats
    logger.info("=== Test d'adresses du système de matching ===")
    try:
        from test.data import sample_addresses
        for address in sample_addresses.SAMPLE_ADDRESSES:
            logger.info(f"Vérification de l'adresse: {address}")
            geocode = client.geocode_address(address)
            if geocode:
                logger.info(f"✅ Adresse valide: {geocode}")
            else:
                logger.warning(f"⚠️ Impossible de géocoder: {address}")
    except ImportError:
        logger.warning("⚠️ Module d'adresses d'exemple non trouvé, test ignoré")
    
    logger.info("=== Tests terminés ===")
    return True

if __name__ == "__main__":
    test_api()
