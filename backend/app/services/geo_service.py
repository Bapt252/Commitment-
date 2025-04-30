import os
import googlemaps
from datetime import datetime
from dotenv import load_dotenv
import logging

# Configuration du logging
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement
load_dotenv()

class GeoService:
    """
    Service pour interagir avec l'API Google Maps
    """
    def __init__(self):
        api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not api_key:
            logger.warning("GOOGLE_MAPS_API_KEY environment variable is not set")
            # Utiliser une clé vide pour le développement, mais les requêtes échoueront
            api_key = ""
        self.gmaps = googlemaps.Client(key=api_key)
    
    def geocode_address(self, address):
        """
        Convertit une adresse en coordonnées géographiques

        Args:
            address (str): Adresse à géocoder

        Returns:
            dict: Coordonnées lat/lng et adresse formatée, ou None en cas d'erreur
        """
        try:
            if not address:
                return None
                
            geocode_result = self.gmaps.geocode(address)
            if geocode_result and len(geocode_result) > 0:
                location = geocode_result[0]['geometry']['location']
                return {
                    "lat": location['lat'],
                    "lng": location['lng'],
                    "formatted_address": geocode_result[0]['formatted_address'],
                    "place_id": geocode_result[0].get('place_id')
                }
            return None
        except Exception as e:
            logger.error(f"Geocoding error: {str(e)}")
            return None
    
    def reverse_geocode(self, lat, lng):
        """
        Convertit des coordonnées en adresse

        Args:
            lat (float): Latitude
            lng (float): Longitude

        Returns:
            dict: Adresse formatée et place_id, ou None en cas d'erreur
        """
        try:
            reverse_geocode_result = self.gmaps.reverse_geocode((lat, lng))
            if reverse_geocode_result and len(reverse_geocode_result) > 0:
                return {
                    "formatted_address": reverse_geocode_result[0]['formatted_address'],
                    "place_id": reverse_geocode_result[0].get('place_id'),
                    "components": reverse_geocode_result[0].get('address_components', [])
                }
            return None
        except Exception as e:
            logger.error(f"Reverse geocoding error: {str(e)}")
            return None
            
    def get_places_nearby(self, lat, lng, radius=5000, keyword=None, place_type=None):
        """
        Recherche des lieux à proximité d'un point

        Args:
            lat (float): Latitude du centre de recherche
            lng (float): Longitude du centre de recherche
            radius (int): Rayon de recherche en mètres (max 50000)
            keyword (str, optional): Mot-clé de recherche
            place_type (str, optional): Type de lieu (ex: "restaurant", "school", etc.)

        Returns:
            list: Liste des lieux trouvés
        """
        try:
            params = {
                'location': (lat, lng),
                'radius': min(radius, 50000)  # Maximum 50km
            }
            
            if keyword:
                params['keyword'] = keyword
            
            if place_type:
                params['type'] = place_type
                
            places_result = self.gmaps.places_nearby(**params)
            
            if places_result and 'results' in places_result:
                return places_result['results']
            return []
        except Exception as e:
            logger.error(f"Places nearby error: {str(e)}")
            return []
            
    def calculate_distance(self, origin, destination, mode="driving"):
        """
        Calcule la distance et le temps de trajet entre deux points

        Args:
            origin (str or tuple): Adresse ou coordonnées d'origine
            destination (str or tuple): Adresse ou coordonnées de destination
            mode (str): Mode de transport (driving, walking, bicycling, transit)

        Returns:
            dict: Informations sur la distance et le temps de trajet
        """
        try:
            matrix = self.gmaps.distance_matrix(
                origins=[origin],
                destinations=[destination],
                mode=mode,
                language="fr",
                units="metric"
            )
            
            if (matrix and 'rows' in matrix and matrix['rows'] and 
                'elements' in matrix['rows'][0] and matrix['rows'][0]['elements']):
                
                element = matrix['rows'][0]['elements'][0]
                
                if element['status'] == 'OK':
                    return {
                        "distance": element['distance'],
                        "duration": element['duration'],
                        "origin": matrix['origin_addresses'][0],
                        "destination": matrix['destination_addresses'][0]
                    }
            
            return None
        except Exception as e:
            logger.error(f"Distance matrix error: {str(e)}")
            return None

# Singleton instance
geo_service = GeoService()
