#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Client Google Maps amélioré avec mode simulation pour Nexten SmartMatch
"""

import os
import logging
import random
import json
import time
from typing import Dict, Optional, List, Tuple, Any
from dotenv import load_dotenv

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleMapsClient:
    """Client pour interagir avec l'API Google Maps"""
    
    def __init__(self, use_mock_mode=False):
        """
        Initialise le client Google Maps
        
        Args:
            use_mock_mode (bool): Si True, utilise des données simulées au lieu d'appeler l'API
        """
        # Charger la clé API depuis les variables d'environnement
        load_dotenv()
        self.api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        self.use_mock_mode = use_mock_mode
        
        if not self.api_key and not self.use_mock_mode:
            logger.warning("⚠️ Clé API Google Maps non trouvée! Les requêtes échoueront.")
        else:
            logger.info("Client Google Maps initialisé avec succès")
            
        # Initialiser le client Google Maps réel si nécessaire
        if not self.use_mock_mode:
            try:
                import googlemaps
                self.gmaps = googlemaps.Client(key=self.api_key)
            except ImportError:
                logger.error("❌ Module 'googlemaps' non installé!")
                self.gmaps = None
            except Exception as e:
                logger.error(f"❌ Erreur lors de l'initialisation du client: {e}")
                self.gmaps = None
        
        # Données simulées
        self._mock_data = self._load_mock_data()
    
    def _load_mock_data(self) -> Dict:
        """Charge ou génère des données simulées pour le développement"""
        # Trajets prédéfinis (origine -> destination -> durée en minutes par mode)
        predefined_routes = {
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
            }
        }
        
        # Géocodage prédéfini (adresse -> lat, lng)
        predefined_geocodes = {
            "Paris, France": (48.856614, 2.3522219),
            "Lyon, France": (45.764043, 4.835659),
            "Versailles, France": (48.8035403, 2.1266886),
            "Nantes, France": (47.218371, -1.553621),
            "Saint-Nazaire, France": (47.2734979, -2.213848),
            "75001, France": (48.86, 2.34),
            "92100, France": (48.9, 2.3),
            "20 Rue de la Paix, 75002 Paris, France": (48.8689111, 2.3297426),
            "10 Place Bellecour, 69002 Lyon, France": (45.7578137, 4.8320114)
        }
        
        # Ajouter des données depuis le fichier sample_addresses.py si disponible
        try:
            from test.data.sample_addresses import SAMPLE_ADDRESSES, SAMPLE_MATCHING_PAIRS
            
            # Ajouter les adresses d'exemple
            for address in SAMPLE_ADDRESSES:
                if address not in predefined_geocodes:
                    # Générer des coordonnées fictives en France
                    predefined_geocodes[address] = (
                        random.uniform(42.0, 51.0),  # latitude en France
                        random.uniform(-4.0, 8.0)    # longitude en France
                    )
            
            # Ajouter les paires de matching
            for pair in SAMPLE_MATCHING_PAIRS:
                key = f"{pair['candidate']}|{pair['company']}"
                if key not in predefined_routes:
                    predefined_routes[key] = pair.get('expected_commute', {})
                    
                    # Si les temps de trajet ne sont pas définis, générer des valeurs
                    if not predefined_routes[key]:
                        predefined_routes[key] = {
                            "driving": random.randint(10, 90),
                            "transit": random.randint(15, 120),
                            "bicycling": random.randint(20, 180),
                            "walking": random.randint(30, 360)
                        }
                        
        except ImportError:
            logger.warning("⚠️ Données d'exemple non disponibles. Utilisation des données prédéfinies seulement.")
            
        return {
            "routes": predefined_routes,
            "geocodes": predefined_geocodes
        }
    
    def get_travel_time(self, origin: str, destination: str, mode: str = "driving") -> int:
        """
        Calcule le temps de trajet entre deux adresses.
        
        Args:
            origin: Adresse d'origine
            destination: Adresse de destination
            mode: Mode de transport (driving, transit, bicycling, walking)
            
        Returns:
            Temps de trajet estimé en minutes, -1 en cas d'erreur
        """
        # Mode simulation
        if self.use_mock_mode:
            return self._mock_get_travel_time(origin, destination, mode)
        
        # Mode réel avec API
        if not self.gmaps:
            logger.error("❌ Client Google Maps non initialisé!")
            return -1
        
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
                return int(duration / 60)
            else:
                logger.warning(f"⚠️ Aucun itinéraire trouvé entre {origin} et {destination}")
                return -1
                
        except Exception as e:
            logger.error(f"❌ Erreur API Google Maps: {e}")
            return -1
    
    def _mock_get_travel_time(self, origin: str, destination: str, mode: str = "driving") -> int:
        """Version simulée de get_travel_time pour le développement"""
        # Rechercher d'abord une correspondance exacte
        key = f"{origin}|{destination}"
        if key in self._mock_data["routes"]:
            return self._mock_data["routes"][key].get(mode, 30)
        
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
        
        Args:
            address: Adresse à géocoder
            
        Returns:
            Tuple (latitude, longitude) ou None en cas d'erreur
        """
        # Mode simulation
        if self.use_mock_mode:
            return self._mock_geocode_address(address)
        
        # Mode réel avec API
        if not self.gmaps:
            logger.error("❌ Client Google Maps non initialisé!")
            return None
        
        try:
            geocode_result = self.gmaps.geocode(address)
            
            if geocode_result and len(geocode_result) > 0:
                location = geocode_result[0].get('geometry', {}).get('location', {})
                lat = location.get('lat')
                lng = location.get('lng')
                
                if lat is not None and lng is not None:
                    return (lat, lng)
                    
            logger.warning(f"⚠️ Impossible de géocoder l'adresse: {address}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur API Google Maps: {e}")
            return None
    
    def _mock_geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """Version simulée de geocode_address pour le développement"""
        # Rechercher une correspondance exacte
        if address in self._mock_data["geocodes"]:
            return self._mock_data["geocodes"][address]
        
        # Générer des coordonnées fictives en France
        lat = random.uniform(42.0, 51.0)  # latitude en France
        lng = random.uniform(-4.0, 8.0)   # longitude en France
        
        # Ajouter à notre cache pour une utilisation future
        self._mock_data["geocodes"][address] = (lat, lng)
        
        return (lat, lng)
    
    def get_distance_matrix(self, origins: List[str], destinations: List[str], 
                           mode: str = "driving") -> Dict:
        """
        Calcule une matrice de distance entre plusieurs origines et destinations
        
        Args:
            origins: Liste d'adresses d'origine
            destinations: Liste d'adresses de destination
            mode: Mode de transport
            
        Returns:
            Dictionnaire contenant la matrice de distance et de durée
        """
        # Mode simulation
        if self.use_mock_mode:
            return self._mock_get_distance_matrix(origins, destinations, mode)
        
        # Mode réel avec API
        if not self.gmaps:
            logger.error("❌ Client Google Maps non initialisé!")
            return {"error": "Client non initialisé"}
        
        try:
            now = int(time.time())
            matrix = self.gmaps.distance_matrix(
                origins=origins,
                destinations=destinations,
                mode=mode,
                departure_time=now
            )
            
            return matrix
            
        except Exception as e:
            logger.error(f"❌ Erreur API Google Maps: {e}")
            return {"error": str(e)}
    
    def _mock_get_distance_matrix(self, origins: List[str], destinations: List[str], 
                                 mode: str = "driving") -> Dict:
        """Version simulée de get_distance_matrix pour le développement"""
        rows = []
        
        for origin in origins:
            row = {"elements": []}
            
            for destination in destinations:
                # Récupérer ou générer un temps de trajet
                travel_time = self._mock_get_travel_time(origin, destination, mode)
                
                # Convertir en secondes pour la cohérence avec l'API
                duration_value = travel_time * 60
                
                # Distance approximative (en mètres, basée sur le temps)
                # Vitesse moyenne approximative selon le mode de transport
                speeds = {
                    "driving": 50,    # km/h
                    "transit": 35,    # km/h
                    "bicycling": 15,  # km/h
                    "walking": 5      # km/h
                }
                speed = speeds.get(mode, 30)
                distance_value = int(travel_time * speed * 1000 / 60)  # en mètres
                
                element = {
                    "distance": {
                        "text": f"{int(distance_value/1000)} km",
                        "value": distance_value
                    },
                    "duration": {
                        "text": f"{travel_time} mins",
                        "value": duration_value
                    },
                    "status": "OK"
                }
                
                row["elements"].append(element)
            
            rows.append(row)
        
        return {
            "rows": rows,
            "status": "OK",
            "origin_addresses": origins,
            "destination_addresses": destinations
        }

# Test simple si exécuté directement
if __name__ == "__main__":
    # Test avec le mode réel
    client_real = GoogleMapsClient()
    time_real = client_real.get_travel_time("Paris, France", "Lyon, France")
    print(f"API: Temps de trajet Paris-Lyon: {time_real} minutes")
    
    # Test avec le mode simulation
    client_mock = GoogleMapsClient(use_mock_mode=True)
    time_mock = client_mock.get_travel_time("Paris, France", "Lyon, France")
    print(f"MOCK: Temps de trajet Paris-Lyon: {time_mock} minutes")
