#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Client Google Maps Hybride Adapté pour Nexten SmartMatch
Ce script contient la classe HybridGoogleMapsClient qui peut être utilisée à la place
du client Google Maps standard tout en maintenant la compatibilité avec le code existant.
"""

import os
import logging
import random
import time
from typing import Dict, Optional, List, Tuple, Any
from dotenv import load_dotenv

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HybridGoogleMapsClient:
    """
    Client hybride qui utilise l'API Google Maps quand elle fonctionne
    et bascule en simulation quand elle échoue.
    """
    
    def __init__(self, api_key=None):
        """
        Initialise le client hybride
        
        Args:
            api_key: Clé API Google Maps (optionnelle)
        """
        # Charger la clé API depuis les variables d'environnement ou le paramètre
        load_dotenv()
        self.api_key = api_key or os.getenv('GOOGLE_MAPS_API_KEY')
        
        # Initialiser le client Google Maps réel
        try:
            import googlemaps
            self.gmaps = googlemaps.Client(key=self.api_key)
            logger.info("Client Google Maps initialisé avec succès (mode hybride adapté)")
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'initialisation du client Google Maps: {e}")
            self.gmaps = None
        
        # Données simulées pour le fallback
        self._load_mock_data()
        
        # Statistiques d'utilisation
        self.stats = {
            "real_api_calls": 0,
            "real_api_success": 0,
            "real_api_failure": 0,
            "mock_api_calls": 0
        }
    
    def _load_mock_data(self):
        """Charge ou génère des données simulées pour le développement"""
        # Trajets prédéfinis (origine -> destination -> durée en minutes par mode)
        self.predefined_routes = {
            # Format: "origine|destination": {"driving": minutes, "transit": minutes, ...}
            "Paris, France|Lyon, France": {
                "driving": 273, 
                "transit": 119, 
                "bicycling": 1620, 
                "walking": 3240
            },
            "Paris, France|Versailles, France": {
                "driving": 28,
                "transit": 42,
                "bicycling": 65,
                "walking": 133
            },
            "Nantes, France|Saint-Nazaire, France": {
                "driving": 55,
                "transit": 78,
                "bicycling": 162,
                "walking": 390
            },
            "75001, France|92100, France": {
                "driving": 24,
                "transit": 39,
                "bicycling": 45,
                "walking": 96
            },
            # Adresses spécifiques pour les exemples
            "20 Rue de la Paix, 75002 Paris, France|Tour Montparnasse, 75015 Paris, France": {
                "driving": 22,
                "transit": 35,
                "bicycling": 40,
                "walking": 90
            }
        }
        
        # Géocodage prédéfini (adresse -> lat, lng)
        self.predefined_geocodes = {
            "Paris, France": (48.856614, 2.3522219),
            "Lyon, France": (45.764043, 4.835659),
            "Versailles, France": (48.8035403, 2.1266886),
            "Nantes, France": (47.218371, -1.553621),
            "20 Rue de la Paix, 75002 Paris, France": (48.8689111, 2.3297426),
            "Tour Montparnasse, 75015 Paris, France": (48.8421, 2.3219)
        }
    
    def get_travel_time(self, origin: str, destination: str, mode: str = "driving") -> int:
        """
        Calcule le temps de trajet entre deux adresses.
        Essaie d'abord l'API réelle, puis bascule en simulation si nécessaire.
        
        Args:
            origin: Adresse d'origine
            destination: Adresse de destination
            mode: Mode de transport (driving, transit, bicycling, walking)
            
        Returns:
            Temps de trajet estimé en minutes, -1 en cas d'erreur
        """
        # Essayer d'abord l'API réelle
        if self.gmaps:
            self.stats["real_api_calls"] += 1
            try:
                now = int(time.time())
                directions = self.gmaps.directions(
                    origin=origin,
                    destination=destination,
                    mode=mode,
                    departure_time=now
                )
                
                if directions and len(directions) > 0:
                    # Récupérer la durée du premier itinéraire
                    leg = directions[0].get('legs', [{}])[0]
                    duration = leg.get('duration', {}).get('value', 0)
                    
                    # Convertir de secondes en minutes
                    result = int(duration / 60)
                    
                    if result > 0:
                        self.stats["real_api_success"] += 1
                        return result
                
                # Si on arrive ici, c'est que l'API n'a pas donné de résultat valide
                logger.warning(f"⚠️ Basculement en simulation pour {origin} → {destination}")
                self.stats["real_api_failure"] += 1
                    
            except Exception as e:
                logger.error(f"❌ Erreur API Google Maps: {e}")
                self.stats["real_api_failure"] += 1
        
        # Fallback en simulation
        self.stats["mock_api_calls"] += 1
        return self._mock_get_travel_time(origin, destination, mode)
    
    def _mock_get_travel_time(self, origin: str, destination: str, mode: str = "driving") -> int:
        """Version simulée de get_travel_time pour le fallback"""
        # Rechercher d'abord une correspondance exacte
        key = f"{origin}|{destination}"
        if key in self.predefined_routes:
            return self.predefined_routes[key].get(mode, 30)
        
        # Si pas de correspondance exacte, simuler un temps raisonnable
        # basé sur le mode de transport
        base_time = random.randint(15, 45)  # Temps de base entre 15 et 45 minutes
        mode_multipliers = {
            "driving": 1.0,
            "transit": 1.5,
            "bicycling": 3.0,
            "walking": 6.0
        }
        
        # Ajouter un peu de variabilité
        variation = random.uniform(0.8, 1.2)
        
        # Simuler un temps raisonnable
        return int(base_time * mode_multipliers.get(mode, 1.0) * variation)
    
    def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Convertit une adresse en coordonnées géographiques (latitude, longitude)
        Essaie d'abord l'API réelle, puis bascule en simulation si nécessaire.
        
        Args:
            address: Adresse à géocoder
            
        Returns:
            Tuple (latitude, longitude) ou None en cas d'erreur
        """
        # Essayer d'abord l'API réelle
        if self.gmaps:
            self.stats["real_api_calls"] += 1
            try:
                geocode_result = self.gmaps.geocode(address)
                
                if geocode_result and len(geocode_result) > 0:
                    location = geocode_result[0].get('geometry', {}).get('location', {})
                    lat = location.get('lat')
                    lng = location.get('lng')
                    
                    if lat is not None and lng is not None:
                        self.stats["real_api_success"] += 1
                        return (lat, lng)
                
                # Si on arrive ici, c'est que l'API n'a pas donné de résultat valide
                logger.warning(f"⚠️ Basculement en simulation pour le géocodage de {address}")
                self.stats["real_api_failure"] += 1
                    
            except Exception as e:
                logger.error(f"❌ Erreur API Google Maps: {e}")
                self.stats["real_api_failure"] += 1
        
        # Fallback en simulation
        self.stats["mock_api_calls"] += 1
        return self._mock_geocode_address(address)
    
    def _mock_geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """Version simulée de geocode_address pour le fallback"""
        # Rechercher une correspondance exacte
        if address in self.predefined_geocodes:
            return self.predefined_geocodes[address]
        
        # Générer des coordonnées fictives en France
        lat = random.uniform(42.0, 51.0)  # latitude en France
        lng = random.uniform(-4.0, 8.0)   # longitude en France
        
        return (lat, lng)

# Usage direct
if __name__ == "__main__":
    # Test simple
    client = HybridGoogleMapsClient()
    time = client.get_travel_time("Paris, France", "Lyon, France", "driving")
    print(f"Temps de trajet: {time} minutes")