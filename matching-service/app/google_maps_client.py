"""
Client Google Maps pour le système Nexten SmartMatch
---------------------------------------------------
Calcule les temps de trajet entre les localisations des candidats 
et des entreprises
en utilisant différents modes de transport (voiture, transports en 
commun, etc.).
Auteur: Claude/Anthropic
Date: "14/05/2025"
"""

import os
import requests
import time
import json
from math import radians, cos, sin, asin, sqrt

# Configuration de l'API Google Maps
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', '')

# Cache pour stocker les résultats des requêtes
# Format: {"origin_destination": {"duration": minutes, "timestamp": unix_timestamp}}
LOCATION_CACHE = {}
CACHE_EXPIRY = 7 * 24 * 60 * 60  # 7 jours en secondes

def calculate_travel_time(origin, destination, mode="driving"):
    """
    Calcule le temps de trajet entre deux adresses en utilisant 
    l\'API Google Maps.
    
    Args:
        origin (str): Adresse d'origine
        destination (str): Adresse de destination
        mode (str): Mode de transport ("driving", "transit", 
"walking", "bicycling")
        
    Returns:
        dict: Résultat avec temps de trajet en minutes, distance en 
km et statut
    """
    # Créer une clé de cache unique incluant le mode de transport
    cache_key = f"{origin}_{destination}_{mode}"
    
    # Vérifier si le résultat est dans le cache et n'est pas expiré
    current_time = time.time()
    if cache_key in LOCATION_CACHE:
        cache_entry = LOCATION_CACHE[cache_key]
        if current_time - cache_entry.get("timestamp", 0) < 
CACHE_EXPIRY:
            return cache_entry["result"]
    
    # Si pas de clé API, utiliser un calcul approché basé sur la 
distance à vol d'oiseau
    if not GOOGLE_MAPS_API_KEY:
        # Estimation approximative basée sur la distance à vol 
d'oiseau
        distance_km = estimate_distance(origin, destination)
        
        # Calculer le temps estimé en fonction du mode de transport
        if mode == "driving":
            # Supposer une vitesse moyenne de 30 km/h en zone 
urbaine
            estimated_time = int(distance_km * 2)  # minutes
        elif mode == "transit":
            # Les transports en commun peuvent être plus lents avec 
les arrêts
            estimated_time = int(distance_km * 3)  # minutes
        elif mode == "walking":
            # Vitesse moyenne de marche: 5 km/h
            estimated_time = int(distance_km * 12)  # minutes
        elif mode == "bicycling":
            # Vitesse moyenne à vélo: 15 km/h
            estimated_time = int(distance_km * 4)  # minutes
        else:
            # Par défaut, utiliser le mode voiture
            estimated_time = int(distance_km * 2)  # minutes
        
        result = {
            "duration": estimated_time,
            "distance": distance_km,
            "status": "APPROXIMATION",
            "origin": origin,
            "destination": destination,
            "mode": mode
        }
        
        # Mettre en cache le résultat
        LOCATION_CACHE[cache_key] = {
            "result": result,
            "timestamp": current_time
        }
        
        return result
    
    # Sinon, utiliser l'API Google Maps
    try:
        url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        params = {
            "origins": origin,
            "destinations": destination,
            "mode": mode,
            "language": "fr-FR",
            "key": GOOGLE_MAPS_API_KEY
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        # Vérifier que la requête a réussi
        if data["status"] == "OK":
            # Extraire le temps de trajet et la distance
            if data["rows"][0]["elements"][0]["status"] == "OK":
                duration_seconds = data["rows"][0]["elements"][0]["duration"]["value"]
                duration_minutes = duration_seconds // 60
                distance_meters = data["rows"][0]["elements"][0]["distance"]["value"]
                distance_km = distance_meters / 1000
                
                result = {
                    "duration": duration_minutes,
                    "distance": round(distance_km, 1),
                    "status": "OK",
                    "origin": origin,
                    "destination": destination,
                    "mode": mode
                }
                
                # Mettre en cache le résultat
                LOCATION_CACHE[cache_key] = {
                    "result": result,
                    "timestamp": current_time
                }
                
                return result
            else:
                # Si le calcul a échoué, utiliser l'estimation
                distance_km = estimate_distance(origin, destination)
                result = {
                    "duration": int(distance_km * 2) if mode == "driving" else int(distance_km * 3),
                    "distance": distance_km,
                    "status": "APPROXIMATION",
                    "origin": origin,
                    "destination": destination,
                    "mode": mode
                }
                
                # Mettre en cache le résultat
                LOCATION_CACHE[cache_key] = {
                    "result": result,
                    "timestamp": current_time
                }
                
                return result
        else:
            # En cas d'erreur API, utiliser l'estimation
            distance_km = estimate_distance(origin, destination)
            result = {
                "duration": int(distance_km * 2) if mode == "driving" else int(distance_km * 3),
                "distance": distance_km,
                "status": "APPROXIMATION",
                "origin": origin,
                "destination": destination,
                "mode": mode
            }
            
            # Mettre en cache le résultat
            LOCATION_CACHE[cache_key] = {
                "result": result,
                "timestamp": current_time
            }
            
            return result
            
    except Exception as e:
        # En cas d'erreur, utiliser l'estimation
        distance_km = estimate_distance(origin, destination)
        result = {
            "duration": int(distance_km * 2) if mode == "driving" else int(distance_km * 3),
            "distance": distance_km,
            "status": "ERROR",
            "error": str(e),
            "origin": origin,
            "destination": destination,
            "mode": mode
        }
        
        # Mettre en cache le résultat
        LOCATION_CACHE[cache_key] = {
            "result": result,
            "timestamp": current_time
        }
        
        return result

def geocode_address(address):
    """
    Convertit une adresse en coordonnées géographiques (latitude, longitude)
    
    Args:
        address (str): Adresse à géocoder
        
    Returns:
        tuple: (latitude, longitude) ou (0, 0) en cas d'erreur
    """
    # Vérifier si on a une clé API
    if not GOOGLE_MAPS_API_KEY:
        # Coordonnées par défaut pour quelques villes françaises
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
        
        # Recherche de ville dans l'adresse
        address_lower = address.lower()
        for city, coords in city_coords.items():
            if city in address_lower:
                return coords
        
        return (0, 0)
    
    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": address,
            "key": GOOGLE_MAPS_API_KEY
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data["status"] == "OK":
            location = data["results"][0]["geometry"]["location"]
            return (location["lat"], location["lng"])
        else:
            return (0, 0)
    except Exception:
        return (0, 0)

def haversine(lon1, lat1, lon2, lat2):
    """
    Calcule la distance à vol d'oiseau entre deux points en km
    en utilisant la formule de Haversine
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

def estimate_distance(origin, destination):
    """
    Estime la distance à vol d'oiseau entre deux adresses
    
    Args:
        origin (str): Adresse d'origine
        destination (str): Adresse de destination
        
    Returns:
        float: Distance estimée en km
    """
    # Géocoder les adresses
    lat1, lon1 = geocode_address(origin)
    lat2, lon2 = geocode_address(destination)
    
    # Si l'une des adresses n'a pas pu être géocodée
    if lat1 == 0 and lon1 == 0 or lat2 == 0 and lon2 == 0:
        return 10.0  # Valeur par défaut de 10 km
    
    # Calculer la distance
    return haversine(lon1, lat1, lon2, lat2)

def calculate_location_score(candidate_address, job_location, max_acceptable_time=120):
    """
    Calcule un score de compatibilité basé sur le temps de trajet
    
    Args:
        candidate_address (str): Adresse du candidat
        job_location (str): Localisation du poste
        max_acceptable_time (int): Temps de trajet maximum acceptable en minutes
        
    Returns:
        float: Score entre 0 et 1
    """
    # Obtenir le temps de trajet
    result = calculate_travel_time(candidate_address, job_location)
    commute_time = result["duration"]
    
    # Calcul du score en fonction du temps de trajet
    if commute_time <= 15:
        # Moins de 15 minutes: excellent
        score = 1.0
    elif commute_time <= 30:
        # Entre 15 et 30 minutes: très bon
        score = 0.8
    elif commute_time <= 45:
        # Entre 30 et 45 minutes: bon
        score = 0.6
    elif commute_time <= 60:
        # Entre 45 et 60 minutes: acceptable
        score = 0.4
    elif commute_time <= 90:
        # Entre 60 et 90 minutes: limite
        score = 0.2
    else:
        # Plus de 90 minutes: problématique
        score = max(0, 1 - (commute_time / max_acceptable_time))
    
    return max(0.0, min(1.0, score))

def get_location_insights(candidate_address, job_location):
    """
    Génère des insights sur la compatibilité de localisation
    
    Args:
        candidate_address (str): Adresse du candidat
        job_location (str): Localisation du poste
        
    Returns:
        dict: Insights sur la compatibilité de localisation
    """
    # Obtenir le temps de trajet
    result = calculate_travel_time(candidate_address, job_location)
    commute_time = result["duration"]
    distance = result["distance"]
    
    # Catégoriser le temps de trajet
    if commute_time <= 15:
        category = "Excellent"
        description = "Trajet très court"
    elif commute_time <= 30:
        category = "Très bon"
        description = "Trajet court et confortable"
    elif commute_time <= 45:
        category = "Bon"
        description = "Trajet de durée modérée"
    elif commute_time <= 60:
        category = "Acceptable"
        description = "Trajet d'une heure environ"
    elif commute_time <= 90:
        category = "Long"
        description = "Trajet assez long"
    else:
        category = "Très long"
        description = "Trajet problématique, potentiellement fatiguant"
    
    return {
        "commute_time": commute_time,
        "distance": distance,
        "category": category,
        "description": description,
        "status": result["status"],
        "mode": result.get("mode", "driving")
    }

def clear_cache():
    """
    Vide le cache des temps de trajet
    """
    global LOCATION_CACHE
    LOCATION_CACHE = {}

# Interface simplifiée pour la compatibilité avec le reste du système
def calculate_commute_time(origin, destination):
    """
    Fonction simplifiée pour calculer le temps de trajet en minutes
    
    Args:
        origin (str): Adresse d'origine
        destination (str): Adresse de destination
        
    Returns:
        int: Temps de trajet en minutes
    """
    result = calculate_travel_time(origin, destination)
    return result["duration"]

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
    
    def get_all_transit_modes(self, origin: str, destination: str) -> dict:
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
            max_time_minutes: Temps maximum acceptable en minutes
            preferred_mode: Mode de transport préféré
            
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
        if travel_time > max_time_minutes:
            return max(0.0, 0.1 - (0.1 * (travel_time - max_time_minutes) / max_time_minutes))
        else:
            return max(0.1, 0.2 - (0.1 * (travel_time - 90) / (max_time_minutes - 90)))
