"""
Location Matcher - Matching basé sur la géolocalisation
------------------------------------------------------
Matcher spécialisé pour évaluer la correspondance géographique
entre candidats et offres d'emploi.

Features:
- Calcul de temps de trajet avec Google Maps API
- Mode de secours avec estimation euclidienne
- Support du travail à distance
- Cache intelligent pour optimiser les performances
- Insights détaillés sur la distance et temps de trajet
"""

import asyncio
import logging
import math
import aiohttp
from typing import Dict, List, Any, Optional, Tuple
from functools import lru_cache

from ..core.models import Candidate, Job, MatchInsight, Location
from ..core.interfaces import BaseMatchEngine, LocationService
from ..core.exceptions import MatcherError, ServiceError
from .base_matcher import BaseMatcher

logger = logging.getLogger(__name__)


class GoogleMapsLocationService:
    """Service de géolocalisation utilisant Google Maps API."""
    
    def __init__(self, api_key: str, timeout: float = 5.0):
        """
        Initialise le service Google Maps.
        
        Args:
            api_key: Clé API Google Maps
            timeout: Timeout pour les requêtes HTTP
        """
        self.api_key = api_key
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Initialise la session HTTP asynchrone."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Ferme la session HTTP."""
        if self.session:
            await self.session.close()
    
    async def calculate_travel_time(
        self, 
        origin: Location, 
        destination: Location,
        mode: str = "driving"
    ) -> Dict[str, Any]:
        """
        Calcule le temps de trajet entre deux points.
        
        Args:
            origin: Localisation d'origine
            destination: Localisation de destination
            mode: Mode de transport (driving, walking, bicycling, transit)
            
        Returns:
            Dict avec distance_km, duration_min, et métadonnées
            
        Raises:
            ServiceError: Si l'API Google Maps échoue
        """
        if not self.session:
            raise ServiceError("Session HTTP non initialisée")
        
        try:
            # Construire les paramètres de la requête
            origin_str = f"{origin.latitude},{origin.longitude}"
            destination_str = f"{destination.latitude},{destination.longitude}"
            
            params = {
                "origins": origin_str,
                "destinations": destination_str,
                "mode": mode,
                "units": "metric",
                "key": self.api_key
            }
            
            # Effectuer la requête API
            url = "https://maps.googleapis.com/maps/api/distancematrix/json"
            async with self.session.get(url, params=params) as response:
                data = await response.json()
            
            # Vérifier la réponse
            if data.get("status") != "OK":
                raise ServiceError(f"Google Maps API error: {data.get('status')}")
            
            # Extraire les résultats
            elements = data["rows"][0]["elements"][0]
            if elements.get("status") != "OK":
                raise ServiceError(f"Route not found: {elements.get('status')}")
            
            # Parser les résultats
            distance_m = elements["distance"]["value"]
            duration_s = elements["duration"]["value"]
            
            return {
                "distance_km": distance_m / 1000,
                "duration_min": duration_s / 60,
                "mode": mode,
                "status": "success",
                "raw_response": elements
            }
            
        except aiohttp.ClientError as e:
            raise ServiceError(f"HTTP error calculating travel time: {str(e)}") from e
        except KeyError as e:
            raise ServiceError(f"Invalid Google Maps API response: {str(e)}") from e


class FallbackLocationService:
    """Service de géolocalisation de secours avec calcul euclidien."""
    
    @staticmethod
    def calculate_travel_time(
        origin: Location, 
        destination: Location,
        mode: str = "driving"
    ) -> Dict[str, Any]:
        """
        Calcule une estimation simplifiée du temps de trajet.
        
        Args:
            origin: Localisation d'origine
            destination: Localisation de destination
            mode: Mode de transport (affecte la vitesse estimée)
            
        Returns:
            Dict avec distance_km, duration_min, et métadonnées
        """
        # Calculer la distance euclidienne (approximation)
        lat_diff = origin.latitude - destination.latitude
        lng_diff = origin.longitude - destination.longitude
        
        # Distance approximative en kilomètres
        # 1 degré ≈ 111 km à l'équateur
        distance_km = math.sqrt(lat_diff**2 + lng_diff**2) * 111
        
        # Vitesses estimées par mode de transport
        speed_kmh = {
            "driving": 50,    # Vitesse moyenne en ville
            "walking": 5,     # Vitesse de marche
            "bicycling": 15,  # Vitesse à vélo
            "transit": 30     # Transport en commun
        }
        
        # Calculer la durée estimée
        speed = speed_kmh.get(mode, 50)
        duration_min = (distance_km / speed) * 60
        
        return {
            "distance_km": distance_km,
            "duration_min": duration_min,
            "mode": mode,
            "status": "estimated",
            "raw_response": None
        }


class LocationMatcher(BaseMatcher):
    """
    Matcher spécialisé pour la correspondance géographique.
    
    Évalue la pertinence d'une offre d'emploi basée sur:
    - Distance géographique entre candidat et poste
    - Temps de trajet avec différents modes de transport
    - Préférences pour le travail à distance
    - Zones géographiques acceptables
    """
    
    def __init__(
        self,
        location_service: Optional[LocationService] = None,
        api_key: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
        cache_size: int = 1000
    ):
        """
        Initialise le matcher de localisation.
        
        Args:
            location_service: Service de géolocalisation personnalisé
            api_key: Clé API Google Maps (si pas de service personnalisé)
            config: Configuration du matcher
            use_cache: Activer le cache pour les calculs de distance
            cache_size: Taille du cache LRU
        """
        super().__init__(config)
        
        # Configuration par défaut
        self.default_config = {
            "max_distance_km": 50,
            "excellent_time_min": 30,
            "good_time_min": 60,
            "acceptable_time_min": 90,
            "transport_modes": ["driving"],
            "remote_work_bonus": 0.2,
            "penalties": {
                "no_remote_when_wanted": 0.5,
                "excessive_distance": 0.3
            }
        }
        self.config = {**self.default_config, **(config or {})}
        
        # Service de géolocalisation
        self.location_service = location_service
        self.api_key = api_key
        self.use_cache = use_cache
        
        # Cache pour les calculs de distance
        if use_cache:
            self._travel_cache: Dict[str, Dict[str, Any]] = {}
            self.cache_size = cache_size
        
        logger.info("LocationMatcher initialisé")
    
    async def calculate_match(self, candidate: Candidate, job: Job) -> float:
        """
        Calcule le score de correspondance géographique.
        
        Args:
            candidate: Profil du candidat
            job: Offre d'emploi
            
        Returns:
            Score entre 0 et 1
        """
        try:
            # Cas spécial : travail à distance
            if self._handle_remote_work(candidate, job):
                # Score parfait si les deux acceptent le remote
                if candidate.preferences.remote_work and job.remote_policy.allowed:
                    return 1.0
                # Pénalité si candidat veut remote mais pas offert
                elif candidate.preferences.remote_work and not job.remote_policy.allowed:
                    return self.config["penalties"]["no_remote_when_wanted"]
                # Bonus si remote offert même si pas demandé
                elif not candidate.preferences.remote_work and job.remote_policy.allowed:
                    base_score = await self._calculate_physical_location_score(candidate, job)
                    return min(1.0, base_score + self.config["remote_work_bonus"])
            
            # Calculer le score basé sur la localisation physique
            return await self._calculate_physical_location_score(candidate, job)
            
        except Exception as e:
            logger.error(f"Erreur dans LocationMatcher: {str(e)}")
            return 0.5  # Score neutre en cas d'erreur
    
    def _handle_remote_work(self, candidate: Candidate, job: Job) -> bool:
        """
        Vérifie si c'est un cas de travail à distance.
        
        Returns:
            True si au moins une des parties propose/accepte le remote
        """
        return (
            (hasattr(candidate.preferences, 'remote_work') and candidate.preferences.remote_work) or
            (hasattr(job, 'remote_policy') and job.remote_policy.allowed)
        )
    
    async def _calculate_physical_location_score(self, candidate: Candidate, job: Job) -> float:
        """
        Calcule le score basé sur la distance/temps de trajet physique.
        
        Args:
            candidate: Profil du candidat
            job: Offre d'emploi
            
        Returns:
            Score entre 0 et 1
        """
        # Vérifier que les localisations sont disponibles
        if not candidate.location or not job.location:
            logger.warning("Localisation manquante pour le candidat ou l'offre")
            return 0.5
        
        # Calculer le temps de trajet
        travel_data = await self._get_travel_time(
            candidate.location, 
            job.location,
            self.config["transport_modes"][0]  # Mode principal
        )
        
        duration_min = travel_data["duration_min"]
        distance_km = travel_data["distance_km"]
        
        # Calculer le score basé sur les seuils configurés
        if duration_min <= self.config["excellent_time_min"]:
            score = 1.0
        elif duration_min <= self.config["good_time_min"]:
            score = 0.8
        elif duration_min <= self.config["acceptable_time_min"]:
            score = 0.6
        elif distance_km <= self.config["max_distance_km"]:
            score = 0.4
        else:
            # Appliquer la pénalité pour distance excessive
            score = self.config["penalties"]["excessive_distance"]
        
        return score
    
    async def _get_travel_time(
        self, 
        origin: Location, 
        destination: Location,
        mode: str = "driving"
    ) -> Dict[str, Any]:
        """
        Obtient le temps de trajet avec gestion du cache.
        
        Args:
            origin: Localisation d'origine
            destination: Localisation de destination
            mode: Mode de transport
            
        Returns:
            Dict avec informations de trajet
        """
        # Clé de cache
        cache_key = f"{origin.latitude},{origin.longitude}-{destination.latitude},{destination.longitude}-{mode}"
        
        # Vérifier le cache si activé
        if self.use_cache and cache_key in self._travel_cache:
            return self._travel_cache[cache_key]
        
        # Calculer le temps de trajet
        if self.location_service:
            # Utiliser le service personnalisé
            travel_data = await self.location_service.calculate_travel_time(origin, destination, mode)
        elif self.api_key:
            # Utiliser Google Maps API
            async with GoogleMapsLocationService(self.api_key) as service:
                travel_data = await service.calculate_travel_time(origin, destination, mode)
        else:
            # Utiliser le service de secours
            travel_data = FallbackLocationService.calculate_travel_time(origin, destination, mode)
        
        # Mettre en cache si activé
        if self.use_cache:
            # Gérer la taille du cache
            if len(self._travel_cache) >= self.cache_size:
                # Supprimer l'élément le plus ancien (FIFO)
                oldest_key = next(iter(self._travel_cache))
                del self._travel_cache[oldest_key]
            
            self._travel_cache[cache_key] = travel_data
        
        return travel_data
    
    async def generate_insights(
        self, 
        candidate: Candidate, 
        job: Job, 
        score: float
    ) -> List[MatchInsight]:
        """
        Génère des insights détaillés sur le matching géographique.
        
        Args:
            candidate: Profil du candidat
            job: Offre d'emploi
            score: Score calculé
            
        Returns:
            Liste d'insights
        """
        insights = []
        
        try:
            # Insight sur le travail à distance
            if candidate.preferences.remote_work and job.remote_policy.allowed:
                insights.append(MatchInsight(
                    category="location",
                    type="strength",
                    title="Compatibilité travail à distance",
                    message="Parfaite adéquation : candidat et employeur acceptent le télétravail",
                    score=1.0,
                    details={
                        "candidate_remote": True,
                        "job_remote": True,
                        "policy": job.remote_policy.policy if hasattr(job.remote_policy, 'policy') else None
                    }
                ))
            elif candidate.preferences.remote_work and not job.remote_policy.allowed:
                insights.append(MatchInsight(
                    category="location",
                    type="weakness",
                    title="Incompatibilité travail à distance",
                    message="Le candidat préfère le télétravail mais ce n'est pas proposé",
                    score=score,
                    details={
                        "candidate_remote": True,
                        "job_remote": False,
                        "impact": "major"
                    }
                ))
            
            # Insights sur la distance physique
            if candidate.location and job.location:
                travel_data = await self._get_travel_time(candidate.location, job.location)
                duration_min = travel_data["duration_min"]
                distance_km = travel_data["distance_km"]
                
                if duration_min <= self.config["excellent_time_min"]:
                    insights.append(MatchInsight(
                        category="location",
                        type="strength",
                        title="Distance optimale",
                        message=f"Temps de trajet excellent : {duration_min:.0f} minutes",
                        score=score,
                        details={
                            "duration_min": duration_min,
                            "distance_km": distance_km,
                            "transport_mode": travel_data["mode"]
                        }
                    ))
                elif duration_min <= self.config["good_time_min"]:
                    insights.append(MatchInsight(
                        category="location",
                        type="neutral",
                        title="Distance acceptable",
                        message=f"Temps de trajet raisonnable : {duration_min:.0f} minutes",
                        score=score,
                        details={
                            "duration_min": duration_min,
                            "distance_km": distance_km,
                            "transport_mode": travel_data["mode"]
                        }
                    ))
                else:
                    insights.append(MatchInsight(
                        category="location",
                        type="weakness",
                        title="Distance importante",
                        message=f"Temps de trajet élevé : {duration_min:.0f} minutes ({distance_km:.1f} km)",
                        score=score,
                        details={
                            "duration_min": duration_min,
                            "distance_km": distance_km,
                            "transport_mode": travel_data["mode"],
                            "suggestion": "Considérer le télétravail partiel"
                        }
                    ))
        
        except Exception as e:
            logger.error(f"Erreur génération insights LocationMatcher: {str(e)}")
            insights.append(MatchInsight(
                category="location",
                type="info",
                title="Analyse géographique limitée",
                message="Impossible d'analyser complètement la correspondance géographique",
                score=score,
                details={"error": str(e)}
            ))
        
        return insights
    
    def clear_cache(self):
        """Vide le cache des calculs de distance."""
        if self.use_cache:
            self._travel_cache.clear()
            logger.info("Cache LocationMatcher vidé")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """
        Retourne les statistiques du cache.
        
        Returns:
            Dict avec les stats du cache
        """
        if not self.use_cache:
            return {"enabled": False}
        
        return {
            "enabled": True,
            "size": len(self._travel_cache),
            "max_size": self.cache_size,
            "usage_percent": (len(self._travel_cache) / self.cache_size) * 100
        }
