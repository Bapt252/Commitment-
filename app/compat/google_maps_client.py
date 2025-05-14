"""Module de compatibilité pour l'API Google Maps.
Ce module fournit une interface pour calculer les temps de trajet entre deux points.
"""

import os
import logging
import requests
import time
from urllib.parse import urlencode

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GoogleMapsClient")

class GoogleMapsClient:
    """
    Client pour l'API Google Maps Distance Matrix.
    Permet de calculer les temps de trajet entre deux adresses.
    """
    
    def __init__(self, api_key=None):
        """
        Initialise le client avec une clé API optionnelle.
        Si aucune clé n'est fournie, tente de la récupérer depuis les variables d'environnement.
        
        Args:
            api_key (str, optional): Clé API Google Maps
        """
        self.api_key = api_key or os.environ.get('GOOGLE_MAPS_API_KEY')
        
        if not self.api_key:
            logger.warning("Aucune clé API Google Maps trouvée. Les fonctionnalités de calcul de trajet ne seront pas disponibles.")
        else:
            logger.info("Client Google Maps initialisé avec succès")
        
        # URL de base pour l'API Distance Matrix
        self.base_url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        
        # Cache pour les temps de trajet
        self.travel_time_cache = {}
    
    def _get_cache_key(self, origin, destination, mode):
        """
        Génère une clé de cache pour une requête.
        
        Args:
            origin (str): Adresse de départ
            destination (str): Adresse d'arrivée
            mode (str): Mode de transport
            
        Returns:
            str: Clé de cache
        """
        return f"{origin}|{destination}|{mode}"
    
    def get_travel_time(self, origin, destination, mode="driving"):
        """
        Calcule le temps de trajet entre deux adresses.
        
        Args:
            origin (str): Adresse de départ
            destination (str): Adresse d'arrivée
            mode (str, optional): Mode de transport (driving, walking, bicycling, transit)
            
        Returns:
            int: Temps de trajet en minutes, -1 en cas d'erreur
        """
        if not self.api_key:
            logger.error("Clé API Google Maps manquante. Impossible de calculer le temps de trajet.")
            return -1
        
        # Vérifier le cache
        cache_key = self._get_cache_key(origin, destination, mode)
        if cache_key in self.travel_time_cache:
            logger.info(f"Utilisation du cache pour le trajet {origin} -> {destination}")
            return self.travel_time_cache[cache_key]
        
        # Construire les paramètres de l'URL
        params = {
            "origins": origin,
            "destinations": destination,
            "mode": mode,
            "key": self.api_key
        }
        
        try:
            # Effectuer la requête
            logger.info(f"Calcul du temps de trajet de {origin} à {destination} en {mode}")
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
                
                # Mettre en cache le résultat
                self.travel_time_cache[cache_key] = duration_minutes
                
                return duration_minutes
            else:
                logger.warning(f"Impossible de calculer le trajet: {data['rows'][0]['elements'][0]['status']}")
                return -1
        
        except Exception as e:
            logger.error(f"Erreur lors du calcul du temps de trajet: {e}")
            return -1
    
    def get_travel_times_batch(self, origins, destinations, mode="driving"):
        """
        Calcule plusieurs temps de trajet en une seule requête.
        
        Args:
            origins (list): Liste des adresses de départ
            destinations (list): Liste des adresses d'arrivée
            mode (str, optional): Mode de transport
            
        Returns:
            list: Liste des temps de trajet en minutes
        """
        if not self.api_key:
            logger.error("Clé API Google Maps manquante. Impossible de calculer les temps de trajet.")
            return [-1] * (len(origins) * len(destinations))
        
        # Limiter le nombre d'origines et destinations par requête
        if len(origins) > 25 or len(destinations) > 25:
            logger.warning("Trop d'origines ou destinations. L'API limite à 25 de chaque.")
            
            # Diviser en plusieurs requêtes si nécessaire
            if len(origins) > 25 and len(destinations) <= 25:
                # Diviser les origines
                results = []
                for i in range(0, len(origins), 25):
                    batch_origins = origins[i:i+25]
                    batch_results = self.get_travel_times_batch(batch_origins, destinations, mode)
                    results.extend(batch_results)
                return results
            elif len(origins) <= 25 and len(destinations) > 25:
                # Diviser les destinations
                results = []
                for i in range(0, len(destinations), 25):
                    batch_destinations = destinations[i:i+25]
                    batch_results = self.get_travel_times_batch(origins, batch_destinations, mode)
                    results.extend(batch_results)
                return results
            else:
                # Diviser les deux
                results = []
                for i in range(0, len(origins), 25):
                    batch_origins = origins[i:i+25]
                    for j in range(0, len(destinations), 25):
                        batch_destinations = destinations[j:j+25]
                        batch_results = self.get_travel_times_batch(batch_origins, batch_destinations, mode)
                        results.extend(batch_results)
                return results
        
        # Construire les paramètres de l'URL
        params = {
            "origins": "|".join(origins),
            "destinations": "|".join(destinations),
            "mode": mode,
            "key": self.api_key
        }
        
        try:
            # Effectuer la requête
            logger.info(f"Calcul de {len(origins)}x{len(destinations)} temps de trajet")
            response = requests.get(self.base_url, params=params)
            
            # Vérifier la réponse
            if response.status_code != 200:
                logger.error(f"Erreur de requête à l'API Google Maps: {response.status_code}")
                return [-1] * (len(origins) * len(destinations))
            
            # Analyser la réponse JSON
            data = response.json()
            
            # Vérifier le statut de la réponse
            if data["status"] != "OK":
                logger.error(f"Erreur API Google Maps: {data['status']}")
                return [-1] * (len(origins) * len(destinations))
            
            # Extraire les temps de trajet
            travel_times = []
            for i, origin_row in enumerate(data["rows"]):
                for j, element in enumerate(origin_row["elements"]):
                    if element["status"] == "OK":
                        duration_seconds = element["duration"]["value"]
                        duration_minutes = round(duration_seconds / 60)
                        
                        # Mettre en cache le résultat
                        cache_key = self._get_cache_key(origins[i], destinations[j], mode)
                        self.travel_time_cache[cache_key] = duration_minutes
                        
                        travel_times.append(duration_minutes)
                    else:
                        logger.warning(f"Impossible de calculer le trajet {origins[i]} -> {destinations[j]}: {element['status']}")
                        travel_times.append(-1)
            
            return travel_times
        
        except Exception as e:
            logger.error(f"Erreur lors du calcul des temps de trajet: {e}")
            return [-1] * (len(origins) * len(destinations))