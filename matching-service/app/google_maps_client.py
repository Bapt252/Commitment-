"""
Client Google Maps pour le système Nexten SmartMatch
---------------------------------------------------
Calcule les temps de trajet entre les localisations des candidats et des entreprises
en utilisant différents modes de transport (voiture, transports en commun, etc.)
Auteur: Claude/Anthropic
Date: 14/05/2025
"""

import os
import logging
import requests
import time
from typing import Dict, Any, List, Optional, Tuple, Union
from functools import lru_cache

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleMapsClient:
    """
    Client pour l'API Google Maps Distance Matrix.
    Permet de calculer les temps de trajet entre deux adresses avec différents modes de transport.
    """
    
    def __init__(self, api_key: str = None, use_cache: bool = True, cache_size: int = 1000):
        """
        Initialise le client avec une clé API et des options de cache.
        
        Args:
            api_key (str, optional): Clé API Google Maps
            use_cache (bool): Utiliser le cache pour les calculs de trajet
            cache_size (int): Taille du cache (nombre d'entrées)
        """
        self.api_key = api_key or os.environ.get('GOOGLE_MAPS_API_KEY')
        
        if not self.api_key:
            logger.warning("Aucune clé API Google Maps trouvée. Les fonctionnalités de calcul de trajet utiliseront des estimations.")
        else:
            logger.info("Client Google Maps initialisé avec succès")
        
        # URL de base pour l'API Distance Matrix
        self.base_url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        
        # Configuration du cache
        self.use_cache = use_cache
        if use_cache:
            # Décorateur de cache pour la méthode get_travel_time
            self.get_travel_time = lru_cache(maxsize=cache_size)(self._get_travel_time)
        else:
            self.get_travel_time = self._get_travel_time
    
    def _get_travel_time(self, origin: str, destination: str, mode: str = "driving") -> int:
        """
        Calcule le temps de trajet entre deux adresses.
        
        Args:
            origin (str): Adresse de départ
            destination (str): Adresse d'arrivée
            mode (str): Mode de transport (driving, transit, walking, bicycling)
            
        Returns:
            int: Temps de trajet en minutes, -1 en cas d'erreur
        """
        if not self.api_key:
            # Estimation basique basée sur une vitesse moyenne et une distance à vol d'oiseau
            logger.warning("Pas de clé API, utilisation d'une estimation basique du temps de trajet")
            return self._estimate_travel_time(origin, destination, mode)
        
        # Construire les paramètres de l'URL
        params = {
            "origins": origin,
            "destinations": destination,
            "mode": mode,
            "key": self.api_key
        }
        
        # Ajouter des paramètres spécifiques pour les transports en commun
        if mode == "transit":
            # Utiliser l'heure actuelle par défaut
            params["departure_time"] = "now"
        
        try:
            # Effectuer la requête
            logger.debug(f"Calcul du temps de trajet de {origin} à {destination} en {mode}")
            response = requests.get(self.base_url, params=params)
            
            # Vérifier la réponse
            if response.status_code != 200:
                logger.error(f"Erreur de requête à l'API Google Maps: {response.status_code}")
                return -1
            
            # Analyser la réponse JSON
            data = response.json()
            
            # Vérifier le statut de la réponse
            if data["status"] != "OK":
                logger.error(f"Erreur API Google Maps: {data['status']}")
                return -1
            
            # Extraire le temps de trajet
            if data["rows"][0]["elements"][0]["status"] == "OK":
                duration_seconds = data["rows"][0]["elements"][0]["duration"]["value"]
                duration_minutes = round(duration_seconds / 60)
                
                # Ajouter des informations supplémentaires pour le mode transit
                if mode == "transit" and "transit_details" in data["rows"][0]["elements"][0]:
                    transit_details = data["rows"][0]["elements"][0]["transit_details"]
                    logger.info(f"Détails du transit: {transit_details}")
                
                return duration_minutes
            else:
                logger.warning(f"Impossible de calculer le trajet: {data['rows'][0]['elements'][0]['status']}")
                return -1
        
        except Exception as e:
            logger.error(f"Erreur lors du calcul du temps de trajet: {e}")
            return -1
    
    def _estimate_travel_time(self, origin: str, destination: str, mode: str = "driving") -> int:
        """
        Estime le temps de trajet sans utiliser l'API Google Maps.
        Utilise une approximation basée sur des vitesses moyennes.
        
        Args:
            origin (str): Adresse de départ
            destination (str): Adresse d'arrivée
            mode (str): Mode de transport
            
        Returns:
            int: Temps de trajet estimé en minutes
        """
        try:
            # Vitesses moyennes approximatives en km/h par mode de transport
            speeds = {
                "driving": 50,     # Vitesse moyenne en ville/périphérie
                "transit": 30,     # Vitesse moyenne des transports en commun
                "walking": 5,      # Vitesse moyenne de marche
                "bicycling": 15    # Vitesse moyenne à vélo
            }
            
            # Si les villes sont identiques (même début d'adresse), retourner un temps court
            if origin.split(',')[0] == destination.split(',')[0]:
                if mode == "driving":
                    return 15  # 15 minutes en voiture dans la même ville
                elif mode == "transit":
                    return 25  # 25 minutes en transport dans la même ville
                elif mode == "walking":
                    return 45  # 45 minutes à pied dans la même ville
                elif mode == "bicycling":
                    return 25  # 25 minutes à vélo dans la même ville
            
            # Pour les villes différentes, faire une estimation plus longue
            else:
                if mode == "driving":
                    return 60  # 1 heure en voiture entre villes
                elif mode == "transit":
                    return 90  # 1h30 en transport entre villes
                elif mode == "walking":
                    return -1  # Trop loin pour marcher
                elif mode == "bicycling":
                    return 180  # 3h à vélo entre villes (peu probable)
            
            return -1  # Par défaut si on ne peut pas estimer
            
        except Exception as e:
            logger.error(f"Erreur lors de l'estimation du temps de trajet: {e}")
            return -1
    
    def get_transit_time(self, origin: str, destination: str) -> int:
        """
        Calcule le temps de trajet en transports en commun entre deux adresses.
        
        Args:
            origin (str): Adresse de départ
            destination (str): Adresse d'arrivée
            
        Returns:
            int: Temps de trajet en minutes, -1 en cas d'erreur
        """
        return self.get_travel_time(origin, destination, mode="transit")
    
    def get_walking_time(self, origin: str, destination: str) -> int:
        """
        Calcule le temps de trajet à pied entre deux adresses.
        
        Args:
            origin (str): Adresse de départ
            destination (str): Adresse d'arrivée
            
        Returns:
            int: Temps de trajet en minutes, -1 en cas d'erreur
        """
        return self.get_travel_time(origin, destination, mode="walking")
    
    def get_bicycling_time(self, origin: str, destination: str) -> int:
        """
        Calcule le temps de trajet à vélo entre deux adresses.
        
        Args:
            origin (str): Adresse de départ
            destination (str): Adresse d'arrivée
            
        Returns:
            int: Temps de trajet en minutes, -1 en cas d'erreur
        """
        return self.get_travel_time(origin, destination, mode="bicycling")
    
    def get_all_transit_modes(self, origin: str, destination: str) -> Dict[str, int]:
        """
        Calcule les temps de trajet pour tous les modes de transport disponibles.
        
        Args:
            origin (str): Adresse de départ
            destination (str): Adresse d'arrivée
            
        Returns:
            Dict[str, int]: Dictionnaire des temps de trajet par mode
        """
        return {
            "driving": self.get_travel_time(origin, destination, mode="driving"),
            "transit": self.get_travel_time(origin, destination, mode="transit"),
            "walking": self.get_travel_time(origin, destination, mode="walking"),
            "bicycling": self.get_travel_time(origin, destination, mode="bicycling")
        }
    
    def calculate_commute_score(self, origin: str, destination: str, 
                               max_time_minutes: int = 60,
                               preferred_mode: str = "driving") -> float:
        """
        Calcule un score de facilité de trajet entre 0 et 1.
        
        Args:
            origin (str): Adresse de départ
            destination (str): Adresse d'arrivée
            max_time_minutes (int): Temps de trajet maximum acceptable en minutes
            preferred_mode (str): Mode de transport préféré
            
        Returns:
            float: Score entre 0 (très difficile) et 1 (très facile)
        """
        # Obtenir les temps de trajet pour différents modes
        driving_time = self.get_travel_time(origin, destination, mode="driving")
        transit_time = self.get_travel_time(origin, destination, mode="transit")
        walking_time = self.get_travel_time(origin, destination, mode="walking")
        
        # Si aucun trajet n'est possible
        if driving_time <= 0 and transit_time <= 0 and walking_time <= 0:
            return 0.0
        
        # Sélectionner le temps pour le mode préféré
        if preferred_mode == "driving":
            preferred_time = driving_time if driving_time > 0 else float('inf')
        elif preferred_mode == "transit":
            preferred_time = transit_time if transit_time > 0 else float('inf')
        elif preferred_mode == "walking":
            preferred_time = walking_time if walking_time > 0 else float('inf')
        else:
            # Par défaut, prendre le meilleur temps
            preferred_time = min(
                driving_time if driving_time > 0 else float('inf'),
                transit_time if transit_time > 0 else float('inf'),
                walking_time if walking_time > 0 else float('inf')
            )
            if preferred_time == float('inf'):
                preferred_time = -1
        
        # Si le mode préféré n'est pas possible
        if preferred_time <= 0:
            return 0.2  # Score de base faible mais pas nul
        
        # Calculer le score basé sur le ratio temps/temps max
        ratio = preferred_time / max_time_minutes
        
        if ratio <= 0.5:  # Moins de la moitié du temps max
            score = 1.0
        elif ratio <= 1.0:  # Entre la moitié et le temps max
            score = 1.0 - 0.5 * (ratio - 0.5) / 0.5
        else:  # Plus que le temps max
            score = 0.5 * max(0, 2.0 - ratio)
        
        # Bonus pour les options multiples de transport
        transport_options = sum(1 for t in [driving_time, transit_time, walking_time] if t > 0 and t <= max_time_minutes * 1.5)
        option_bonus = min(0.2, transport_options * 0.1)  # Max 0.2 de bonus
        
        return min(1.0, score + option_bonus)
"""