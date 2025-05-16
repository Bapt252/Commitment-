"""
Client Google Maps minimaliste pour SmartMatch
--------------------------------------------
Version simplifiée et robuste du client Google Maps pour 
le calcul des temps de trajet, sans dépendances complexes.

Auteur: Claude/Anthropic
Date: "16/05/2025"
"""

import os
import requests
import logging
from math import radians, cos, sin, asin, sqrt

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MinimalMapsClient:
    """Client minimal pour l'API Google Maps Distance Matrix"""
    
    def __init__(self, api_key=None):
        """Initialiser le client avec une clé API"""
        self.api_key = api_key or os.environ.get('GOOGLE_MAPS_API_KEY', '')
        if not self.api_key:
            logger.warning("Aucune clé API Google Maps trouvée")
        else:
            logger.info("Client Google Maps initialisé")
    
    def get_travel_time(self, origin, destination, mode="driving"):
        """
        Calculer le temps de trajet entre deux adresses.
        
        Args:
            origin (str): Adresse de départ
            destination (str): Adresse d'arrivée
            mode (str): Mode de transport ('driving', 'transit', 'walking', 'bicycling')
            
        Returns:
            int: Temps de trajet en minutes, -1 en cas d'erreur
        """
        if not self.api_key:
            # Estimations basiques si pas de clé API
            if origin.split(',')[0] == destination.split(',')[0]:
                # Même ville
                if mode == "driving": return 20
                if mode == "transit": return 30
                if mode == "bicycling": return 40
                if mode == "walking": return 90
                return 20
            else:
                # Villes différentes
                if mode == "driving": return 60
                if mode == "transit": return 90
                if mode == "bicycling": return 180
                if mode == "walking": return -1  # Trop loin pour marcher
                return 60
        
        url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        params = {
            "origins": origin,
            "destinations": destination,
            "mode": mode,
            "key": self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if data["status"] == "OK" and data["rows"][0]["elements"][0]["status"] == "OK":
                duration_seconds = data["rows"][0]["elements"][0]["duration"]["value"]
                return duration_seconds // 60  # Convertir en minutes
            else:
                logger.warning(f"Erreur API: {data.get('status')}")
                return self._estimate_travel_time(origin, destination, mode)
        except Exception as e:
            logger.error(f"Erreur lors de l'appel à l'API: {e}")
            return self._estimate_travel_time(origin, destination, mode)
    
    def _estimate_travel_time(self, origin, destination, mode="driving"):
        """
        Estimer le temps de trajet sans utiliser l'API.
        
        Args:
            origin (str): Adresse de départ
            destination (str): Adresse d'arrivée
            mode (str): Mode de transport
            
        Returns:
            int: Temps de trajet estimé en minutes
        """
        # Vérifier si les adresses sont dans la même ville
        origin_city = origin.split(',')[0].strip().lower()
        destination_city = destination.split(',')[0].strip().lower()
        
        if origin_city == destination_city:
            # Même ville: estimation basée sur la taille moyenne des villes françaises
            if mode == "driving": return 20
            if mode == "transit": return 30
            if mode == "bicycling": return 40
            if mode == "walking": return 90
            return 20
        else:
            # Utiliser la distance approximative entre les villes françaises
            distance_km = self._estimate_distance(origin, destination)
            
            # Calculer le temps en fonction du mode de transport
            if mode == "driving":
                # Vitesse moyenne en voiture: 70 km/h
                return int(distance_km / 70 * 60)
            elif mode == "transit":
                # Vitesse moyenne en transport: 50 km/h
                return int(distance_km / 50 * 60)
            elif mode == "bicycling":
                # Vitesse moyenne à vélo: 15 km/h
                if distance_km > 30: return -1  # Trop loin pour le vélo
                return int(distance_km / 15 * 60)
            elif mode == "walking":
                # Vitesse moyenne à pied: 5 km/h
                if distance_km > 10: return -1  # Trop loin pour marcher
                return int(distance_km / 5 * 60)
            else:
                return int(distance_km / 60 * 60)  # Vitesse par défaut: 60 km/h
    
    def _estimate_distance(self, origin, destination):
        """
        Estimer la distance entre deux adresses.
        
        Args:
            origin (str): Adresse de départ
            destination (str): Adresse d'arrivée
            
        Returns:
            float: Distance estimée en km
        """
        # Coordonnées approximatives de quelques villes françaises
        city_coords = {
            "paris": (48.8566, 2.3522),
            "lyon": (45.7578, 4.8320),
            "marseille": (43.2965, 5.3698),
            "toulouse": (43.6047, 1.4442),
            "nice": (43.7102, 7.2620),
            "nantes": (47.2184, -1.5536),
            "strasbourg": (48.5734, 7.7521),
            "bordeaux": (44.8378, -0.5792),
            "lille": (50.6292, 3.0573),
            "grenoble": (45.1885, 5.7245)
        }
        
        # Extraire les villes des adresses
        origin_city = origin.split(',')[0].strip().lower()
        destination_city = destination.split(',')[0].strip().lower()
        
        # Récupérer les coordonnées
        origin_coords = city_coords.get(origin_city, (0, 0))
        dest_coords = city_coords.get(destination_city, (0, 0))
        
        # Si l'une des villes n'est pas dans notre dictionnaire
        if origin_coords == (0, 0) or dest_coords == (0, 0):
            # Distance par défaut entre villes françaises
            return 400
        
        # Calculer la distance avec la formule de Haversine
        return self._haversine(origin_coords[1], origin_coords[0], dest_coords[1], dest_coords[0])
    
    def _haversine(self, lon1, lat1, lon2, lat2):
        """
        Calculer la distance entre deux points géographiques.
        
        Args:
            lon1, lat1: Coordonnées du premier point
            lon2, lat2: Coordonnées du deuxième point
            
        Returns:
            float: Distance en km
        """
        # Convertir en radians
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        
        # Formule de Haversine
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Rayon de la Terre en km
        
        return c * r
    
    def calculate_commute_score(self, origin, destination, max_time=60, preferred_mode="driving"):
        """
        Calculer un score de facilité de trajet entre 0 et 1.
        
        Args:
            origin (str): Adresse de départ
            destination (str): Adresse d'arrivée
            max_time (int): Temps maximum acceptable en minutes
            preferred_mode (str): Mode de transport préféré
            
        Returns:
            float: Score entre 0 et 1 (1 = excellent, 0 = très mauvais)
        """
        # Obtenir le temps de trajet
        travel_time = self.get_travel_time(origin, destination, mode=preferred_mode)
        
        # Si impossible de calculer le trajet
        if travel_time < 0:
            return 0.0
        
        # Trajet très court (< 15 min): excellent
        if travel_time <= 15:
            return 1.0
        
        # Trajet raisonnable (< 30 min): très bon
        if travel_time <= 30:
            return 0.8
        
        # Trajet acceptable (< 45 min): bon
        if travel_time <= 45:
            return 0.6
        
        # Trajet long mais acceptable (< 60 min): moyen
        if travel_time <= 60:
            return 0.4
            
        # Trajet long (< 90 min): passable
        if travel_time <= 90:
            return 0.2
        
        # Trajet très long: utiliser une échelle décroissante
        # Si le temps est égal au max, score = 0.1
        # Si le temps > max, score tend vers 0
        if travel_time > max_time:
            return max(0.0, 0.1 - (0.1 * (travel_time - max_time) / max_time))
        else:
            return max(0.1, 0.2 - (0.1 * (travel_time - 90) / (max_time - 90)))
    
    def get_all_transit_modes(self, origin, destination):
        """
        Calculer les temps de trajet pour tous les modes de transport.
        
        Args:
            origin (str): Adresse de départ
            destination (str): Adresse d'arrivée
            
        Returns:
            dict: Dictionnaire des temps de trajet par mode
        """
        return {
            "driving": self.get_travel_time(origin, destination, mode="driving"),
            "transit": self.get_travel_time(origin, destination, mode="transit"),
            "walking": self.get_travel_time(origin, destination, mode="walking"),
            "bicycling": self.get_travel_time(origin, destination, mode="bicycling")
        }

# Test simple si exécuté directement
if __name__ == "__main__":
    client = MinimalMapsClient()
    origin = "Paris, France"
    destination = "Lyon, France"
    print(f"Temps de trajet de {origin} à {destination}: {client.get_travel_time(origin, destination)} minutes")
    print(f"Score de trajet: {client.calculate_commute_score(origin, destination):.2f}/1.00")
    print("Temps par mode de transport:")
    for mode, time in client.get_all_transit_modes(origin, destination).items():
        print(f"- {mode}: {time} minutes")
