#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Client Google Maps amélioré pour Nexten SmartMatch avec gestion avancée de cache et quotas
"""

import os
import logging
import random
import json
import time
from typing import Dict, Optional, List, Tuple, Any
from dotenv import load_dotenv
import threading
import datetime
from app.maps_cache import MapsCache

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleMapsClient:
    """Client pour interagir avec l'API Google Maps avec gestion de cache et quotas"""
    
    def __init__(self, api_key=None, use_mock_mode=False, use_hybrid_mode=True, 
                 redis_url=None, rate_limit=500):
        """
        Initialise le client Google Maps avec gestion de cache et quotas
        
        Args:
            api_key: Clé API Google Maps (optionnelle)
            use_mock_mode (bool): Si True, utilise uniquement des données simulées
            use_hybrid_mode (bool): Si True, bascule entre API réelle et simulation
            redis_url (str): URL de connexion Redis pour le cache
            rate_limit (int): Limite d'appels à l'API Google Maps par jour
        """
        # Charger la clé API depuis les variables d'environnement ou le paramètre
        load_dotenv()
        self.api_key = api_key or os.getenv('GOOGLE_MAPS_API_KEY')
        self.use_mock_mode = use_mock_mode
        self.use_hybrid_mode = use_hybrid_mode and not use_mock_mode  # Hybride uniquement si pas en mode simulation pur
        
        # Initialiser le gestionnaire de cache
        self.cache = MapsCache(redis_url=redis_url)
        
        # Gestion des quotas
        self.rate_limit = rate_limit
        self.daily_usage = 0
        self.usage_lock = threading.Lock()
        self.last_reset_date = datetime.date.today()
        
        if not self.api_key and not self.use_mock_mode:
            logger.warning("⚠️ Clé API Google Maps non trouvée! Les requêtes échoueront.")
        else:
            if self.use_mock_mode:
                logger.info("Client Google Maps initialisé en mode simulation")
            elif self.use_hybrid_mode:
                logger.info("Client Google Maps initialisé en mode hybride (API + simulation)")
            else:
                logger.info("Client Google Maps initialisé en mode API uniquement")
            
        # Initialiser le client Google Maps réel si nécessaire
        if not self.use_mock_mode or self.use_hybrid_mode:
            try:
                import googlemaps
                self.gmaps = googlemaps.Client(key=self.api_key)
            except ImportError:
                logger.error("❌ Module 'googlemaps' non installé!")
                self.gmaps = None
                if not self.use_mock_mode and not self.use_hybrid_mode:
                    # Activer automatiquement le mode hybride si le module n'est pas installé
                    logger.warning("⚠️ Activation automatique du mode hybride suite à l'erreur d'import")
                    self.use_hybrid_mode = True
                    self.use_mock_mode = True
            except Exception as e:
                logger.error(f"❌ Erreur lors de l'initialisation du client: {e}")
                self.gmaps = None
                if not self.use_mock_mode and not self.use_hybrid_mode:
                    # Activer automatiquement le mode hybride si l'initialisation échoue
                    logger.warning("⚠️ Activation automatique du mode hybride suite à l'erreur d'initialisation")
                    self.use_hybrid_mode = True
                    self.use_mock_mode = True
        
        # Données simulées
        self._mock_data = self._load_mock_data()
        
        # Statistiques d'utilisation
        self.stats = {
            "real_api_calls": 0,
            "real_api_success": 0,
            "real_api_failure": 0,
            "mock_api_calls": 0,
            "cached_results": 0,
            "hybrid_fallbacks": 0,
            "quota_exceeded_today": False
        }
    
    def _check_and_update_usage(self):
        """Vérifie et met à jour l'utilisation quotidienne de l'API"""
        with self.usage_lock:
            # Réinitialiser le compteur si on est un nouveau jour
            today = datetime.date.today()
            if today > self.last_reset_date:
                self.daily_usage = 0
                self.last_reset_date = today
                self.stats["quota_exceeded_today"] = False
                logger.info(f"Compteur d'utilisation API réinitialisé pour la journée du {today}")
            
            # Vérifier si le quota est dépassé
            if self.daily_usage >= self.rate_limit:
                self.stats["quota_exceeded_today"] = True
                return False
            
            # Incrémenter le compteur
            self.daily_usage += 1
            return True
    
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
            "10 Place Bellecour, 69002 Lyon, France": (45.7578137, 4.8320114),
            # Adresses spécifiques pour l'exemple d'intégration
            "Tour Montparnasse, 75015 Paris, France": (48.8421, 2.3219),
            "15 Quai des Bateliers, 67000 Strasbourg, France": (48.5809, 7.7523)
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
            logger.debug("Module d'adresses d'exemple non disponible. Utilisation des données prédéfinies.")
            
        return {
            "routes": predefined_routes,
            "geocodes": predefined_geocodes
        }
    
    def get_travel_time(self, origin: str, destination: str, mode: str = "driving") -> int:
        """
        Calcule le temps de trajet entre deux adresses.
        Version avec cache qui essaie d'abord le cache, puis l'API.
        
        Args:
            origin: Adresse d'origine
            destination: Adresse de destination
            mode: Mode de transport (driving, transit, bicycling, walking)
            
        Returns:
            Temps de trajet estimé en minutes, -1 en cas d'erreur
        """
        # Vérifier d'abord le cache
        cached_result = self.cache.get(
            "travel_time",
            origin=origin,
            destination=destination,
            mode=mode
        )
        
        if cached_result is not None:
            self.stats["cached_results"] += 1
            logger.debug(f"Résultat trouvé en cache pour {origin} → {destination} ({mode})")
            return cached_result
        
        # Mode 100% simulation
        if self.use_mock_mode and not self.use_hybrid_mode:
            self.stats["mock_api_calls"] += 1
            time_result = self._mock_get_travel_time(origin, destination, mode)
            
            # Mettre en cache le résultat simulé
            if time_result > 0:
                self.cache.set(
                    "travel_time",
                    time_result,
                    origin=origin,
                    destination=destination,
                    mode=mode
                )
            
            return time_result
        
        # Mode API réelle ou hybride
        if self.gmaps:
            # Vérifier les quotas
            if not self._check_and_update_usage() and self.use_hybrid_mode:
                logger.warning("⚠️ Quota d'API dépassé, basculement en simulation")
                self.stats["hybrid_fallbacks"] += 1
                time_result = self._mock_get_travel_time(origin, destination, mode)
                
                # Mettre en cache le résultat simulé
                if time_result > 0:
                    self.cache.set(
                        "travel_time",
                        time_result,
                        origin=origin,
                        destination=destination,
                        mode=mode
                    )
                
                return time_result
            
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
                        
                        # Mettre en cache le résultat
                        self.cache.set(
                            "travel_time",
                            result,
                            origin=origin,
                            destination=destination,
                            mode=mode
                        )
                        
                        return result
                    else:
                        # Résultat invalide (0 minutes)
                        if self.use_hybrid_mode:
                            logger.warning(f"⚠️ Résultat API invalide pour {origin} → {destination}, basculement en simulation")
                            self.stats["hybrid_fallbacks"] += 1
                            time_result = self._mock_get_travel_time(origin, destination, mode)
                            
                            # Mettre en cache le résultat simulé
                            if time_result > 0:
                                self.cache.set(
                                    "travel_time",
                                    time_result,
                                    origin=origin,
                                    destination=destination,
                                    mode=mode
                                )
                            
                            return time_result
                        self.stats["real_api_failure"] += 1
                        return -1
                else:
                    logger.warning(f"⚠️ Aucun itinéraire trouvé entre {origin} et {destination}")
                    if self.use_hybrid_mode:
                        logger.info(f"Basculement en simulation pour {origin} → {destination} ({mode})")
                        self.stats["hybrid_fallbacks"] += 1
                        time_result = self._mock_get_travel_time(origin, destination, mode)
                        
                        # Mettre en cache le résultat simulé
                        if time_result > 0:
                            self.cache.set(
                                "travel_time",
                                time_result,
                                origin=origin,
                                destination=destination,
                                mode=mode
                            )
                        
                        return time_result
                    self.stats["real_api_failure"] += 1
                    return -1
                    
            except Exception as e:
                logger.error(f"❌ Erreur API Google Maps: {e}")
                if self.use_hybrid_mode:
                    logger.info(f"Basculement en simulation suite à une erreur pour {origin} → {destination}")
                    self.stats["hybrid_fallbacks"] += 1
                    time_result = self._mock_get_travel_time(origin, destination, mode)
                    
                    # Mettre en cache le résultat simulé
                    if time_result > 0:
                        self.cache.set(
                            "travel_time",
                            time_result,
                            origin=origin,
                            destination=destination,
                            mode=mode
                        )
                    
                    return time_result
                self.stats["real_api_failure"] += 1
                return -1
        else:
            # Client non initialisé
            logger.error("❌ Client Google Maps non initialisé!")
            if self.use_hybrid_mode:
                logger.info("Basculement en simulation car le client n'est pas initialisé")
                self.stats["hybrid_fallbacks"] += 1
                time_result = self._mock_get_travel_time(origin, destination, mode)
                
                # Mettre en cache le résultat simulé
                if time_result > 0:
                    self.cache.set(
                        "travel_time",
                        time_result,
                        origin=origin,
                        destination=destination,
                        mode=mode
                    )
                
                return time_result
            self.stats["real_api_failure"] += 1
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
        Version avec cache qui essaie d'abord le cache, puis l'API.
        
        Args:
            address: Adresse à géocoder
            
        Returns:
            Tuple (latitude, longitude) ou None en cas d'erreur
        """
        # Vérifier d'abord le cache
        cached_result = self.cache.get("geocode", address=address)
        
        if cached_result is not None:
            self.stats["cached_results"] += 1
            logger.debug(f"Résultat de géocodage trouvé en cache pour {address}")
            return tuple(cached_result)
        
        # Mode 100% simulation
        if self.use_mock_mode and not self.use_hybrid_mode:
            self.stats["mock_api_calls"] += 1
            geocode_result = self._mock_geocode_address(address)
            
            # Mettre en cache le résultat simulé
            if geocode_result:
                self.cache.set("geocode", geocode_result, address=address)
            
            return geocode_result
        
        # Mode API réelle ou hybride
        if self.gmaps:
            # Vérifier les quotas
            if not self._check_and_update_usage() and self.use_hybrid_mode:
                logger.warning("⚠️ Quota d'API dépassé, basculement en simulation pour le géocodage")
                self.stats["hybrid_fallbacks"] += 1
                geocode_result = self._mock_geocode_address(address)
                
                # Mettre en cache le résultat simulé
                if geocode_result:
                    self.cache.set("geocode", geocode_result, address=address)
                
                return geocode_result
            
            self.stats["real_api_calls"] += 1
            try:
                geocode_result = self.gmaps.geocode(address)
                
                if geocode_result and len(geocode_result) > 0:
                    location = geocode_result[0].get('geometry', {}).get('location', {})
                    lat = location.get('lat')
                    lng = location.get('lng')
                    
                    if lat is not None and lng is not None:
                        self.stats["real_api_success"] += 1
                        result = (lat, lng)
                        
                        # Mettre en cache le résultat
                        self.cache.set("geocode", result, address=address)
                        
                        return result
                        
                logger.warning(f"⚠️ Impossible de géocoder l'adresse: {address}")
                if self.use_hybrid_mode:
                    logger.info(f"Basculement en simulation pour le géocodage de: {address}")
                    self.stats["hybrid_fallbacks"] += 1
                    geocode_result = self._mock_geocode_address(address)
                    
                    # Mettre en cache le résultat simulé
                    if geocode_result:
                        self.cache.set("geocode", geocode_result, address=address)
                    
                    return geocode_result
                self.stats["real_api_failure"] += 1
                return None
                
            except Exception as e:
                logger.error(f"❌ Erreur API Google Maps: {e}")
                if self.use_hybrid_mode:
                    logger.info(f"Basculement en simulation pour le géocodage suite à une erreur")
                    self.stats["hybrid_fallbacks"] += 1
                    geocode_result = self._mock_geocode_address(address)
                    
                    # Mettre en cache le résultat simulé
                    if geocode_result:
                        self.cache.set("geocode", geocode_result, address=address)
                    
                    return geocode_result
                self.stats["real_api_failure"] += 1
                return None
        else:
            # Client non initialisé
            logger.error("❌ Client Google Maps non initialisé!")
            if self.use_hybrid_mode:
                logger.info("Basculement en simulation car le client n'est pas initialisé")
                self.stats["hybrid_fallbacks"] += 1
                geocode_result = self._mock_geocode_address(address)
                
                # Mettre en cache le résultat simulé
                if geocode_result:
                    self.cache.set("geocode", geocode_result, address=address)
                
                return geocode_result
            self.stats["real_api_failure"] += 1
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
        Version avec cache qui essaie d'abord le cache, puis l'API.
        
        Args:
            origins: Liste d'adresses d'origine
            destinations: Liste d'adresses de destination
            mode: Mode de transport
            
        Returns:
            Dictionnaire contenant la matrice de distance et de durée
        """
        # Créer une clé de cache composite pour la matrice
        cache_key = f"{','.join(origins)}|{','.join(destinations)}|{mode}"
        
        # Vérifier d'abord le cache
        cached_result = self.cache.get(
            "distance_matrix",
            origins=origins,
            destinations=destinations,
            mode=mode
        )
        
        if cached_result is not None:
            self.stats["cached_results"] += 1
            logger.debug(f"Résultat de matrice de distance trouvé en cache")
            return cached_result
        
        # Mode 100% simulation
        if self.use_mock_mode and not self.use_hybrid_mode:
            self.stats["mock_api_calls"] += 1
            matrix_result = self._mock_get_distance_matrix(origins, destinations, mode)
            
            # Mettre en cache le résultat simulé
            self.cache.set("distance_matrix", matrix_result, 
                           origins=origins, destinations=destinations, mode=mode)
            
            return matrix_result
        
        # Mode API réelle ou hybride
        if self.gmaps:
            # Vérifier les quotas - cet appel est plus coûteux (O(n*m) entrées)
            cost_factor = len(origins) * len(destinations)
            can_use_api = True
            
            with self.usage_lock:
                if self.daily_usage + cost_factor > self.rate_limit:
                    if self.use_hybrid_mode:
                        can_use_api = False
                    else:
                        # En mode API uniquement, on utilise quand même l'API si possible
                        remaining = max(0, self.rate_limit - self.daily_usage)
                        if remaining <= 0:
                            can_use_api = False
            
            if not can_use_api and self.use_hybrid_mode:
                logger.warning("⚠️ Quota d'API insuffisant pour la matrice de distance, basculement en simulation")
                self.stats["hybrid_fallbacks"] += 1
                matrix_result = self._mock_get_distance_matrix(origins, destinations, mode)
                
                # Mettre en cache le résultat simulé
                self.cache.set("distance_matrix", matrix_result, 
                               origins=origins, destinations=destinations, mode=mode)
                
                return matrix_result
            
            self.stats["real_api_calls"] += 1
            # Incrémenter le compteur d'utilisation
            with self.usage_lock:
                self.daily_usage += cost_factor
            
            try:
                now = int(time.time())
                matrix = self.gmaps.distance_matrix(
                    origins=origins,
                    destinations=destinations,
                    mode=mode,
                    departure_time=now
                )
                
                # Vérifier si la réponse est valide
                status = matrix.get("status", "")
                if status == "OK":
                    self.stats["real_api_success"] += 1
                    
                    # Mettre en cache le résultat
                    self.cache.set("distance_matrix", matrix, 
                                   origins=origins, destinations=destinations, mode=mode)
                    
                    return matrix
                else:
                    logger.warning(f"⚠️ Statut de la matrice de distance: {status}")
                    if self.use_hybrid_mode:
                        logger.info(f"Basculement en simulation pour la matrice de distance")
                        self.stats["hybrid_fallbacks"] += 1
                        matrix_result = self._mock_get_distance_matrix(origins, destinations, mode)
                        
                        # Mettre en cache le résultat simulé
                        self.cache.set("distance_matrix", matrix_result, 
                                      origins=origins, destinations=destinations, mode=mode)
                        
                        return matrix_result
                    self.stats["real_api_failure"] += 1
                    return {"error": f"Statut API: {status}"}
                
            except Exception as e:
                logger.error(f"❌ Erreur API Google Maps: {e}")
                if self.use_hybrid_mode:
                    logger.info(f"Basculement en simulation pour la matrice de distance suite à une erreur")
                    self.stats["hybrid_fallbacks"] += 1
                    matrix_result = self._mock_get_distance_matrix(origins, destinations, mode)
                    
                    # Mettre en cache le résultat simulé
                    self.cache.set("distance_matrix", matrix_result, 
                                  origins=origins, destinations=destinations, mode=mode)
                    
                    return matrix_result
                self.stats["real_api_failure"] += 1
                return {"error": str(e)}
        else:
            # Client non initialisé
            logger.error("❌ Client Google Maps non initialisé!")
            if self.use_hybrid_mode:
                logger.info("Basculement en simulation car le client n'est pas initialisé")
                self.stats["hybrid_fallbacks"] += 1
                matrix_result = self._mock_get_distance_matrix(origins, destinations, mode)
                
                # Mettre en cache le résultat simulé
                self.cache.set("distance_matrix", matrix_result, 
                               origins=origins, destinations=destinations, mode=mode)
                
                return matrix_result
            self.stats["real_api_failure"] += 1
            return {"error": "Client non initialisé"}
    
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
    
    def get_usage_stats(self) -> Dict:
        """Renvoie les statistiques d'utilisation du client et du cache"""
        # Calculer des pourcentages 
        total_real_calls = self.stats["real_api_success"] + self.stats["real_api_failure"]
        success_rate = (self.stats["real_api_success"] / total_real_calls * 100) if total_real_calls > 0 else 0
        
        # Obtenir les statistiques du cache
        cache_stats = self.cache.get_stats()
        
        stats = {
            **self.stats,
            "success_rate": round(success_rate, 2),
            "total_calls": self.stats["real_api_calls"] + self.stats["mock_api_calls"] + self.stats["cached_results"],
            "mode": "simulation" if self.use_mock_mode and not self.use_hybrid_mode else 
                    "hybride" if self.use_hybrid_mode else "API uniquement",
            "daily_usage": self.daily_usage,
            "rate_limit": self.rate_limit,
            "rate_limit_remaining": max(0, self.rate_limit - self.daily_usage),
            "cache": cache_stats
        }
        
        return stats

# Test simple si exécuté directement
if __name__ == "__main__":
    # Test avec le mode hybride
    client_hybrid = GoogleMapsClient(use_hybrid_mode=True, rate_limit=100)
    
    print("\n=== TEST DU CLIENT HYBRIDE ===")
    
    # Test de plusieurs trajets
    test_routes = [
        ("Paris, France", "Lyon, France", "driving"),
        ("Paris, France", "Versailles, France", "bicycling"),
        ("Nantes, France", "Saint-Nazaire, France", "transit"),
        ("75001, France", "92100, France", "walking")
    ]
    
    for origin, destination, mode in test_routes:
        time = client_hybrid.get_travel_time(origin, destination, mode)
        print(f"Temps de trajet en {mode} de {origin} à {destination}: {time} minutes")
    
    # Tester le cache en refaisant une requête
    print("\n=== TEST DU CACHE ===")
    cached_time = client_hybrid.get_travel_time("Paris, France", "Lyon, France", "driving")
    print(f"Temps mis en cache: {cached_time} minutes")
    
    # Affichage des statistiques
    print("\nStatistiques d'utilisation:")
    for key, value in client_hybrid.get_usage_stats().items():
        if isinstance(value, dict):
            print(f"- {key}:")
            for subkey, subvalue in value.items():
                print(f"  - {subkey}: {subvalue}")
        else:
            print(f"- {key}: {value}")
