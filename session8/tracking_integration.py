"""
Module d'intégration avec le système de tracking existant.

Ce module gère la récupération des données de tracking utilisateur pour
le module d'analyse comportementale et de profilage.
"""

import logging
import json
import os
import time
import requests
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import traceback

# Import des configurations
from session8.config import CONFIG

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class TrackingIntegration:
    """
    Classe gérant l'intégration avec le système de tracking existant.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialise l'intégration avec le système de tracking.
        
        Args:
            config: Configuration spécifique (si None, utilise CONFIG["tracking_integration"])
        """
        self.config = config or CONFIG["tracking_integration"]
        self.tracking_url = self.config["tracking_service_url"]
        self.auth_token = self.config["auth_token"]
        self.batch_size = self.config["batch_size"]
        self.timeout = self.config["timeout_seconds"]
        self.max_retries = self.config["max_retries"]
        self.retry_delay = self.config["retry_delay_seconds"]
        
        # Cache pour les données récupérées récemment
        self.data_cache = {}
        self.cache_timestamp = {}
        
        logger.info(f"TrackingIntegration initialized with endpoint {self.tracking_url}")
    
    def get_user_events(self, user_id: str, start_date: Optional[datetime] = None, 
                       end_date: Optional[datetime] = None, event_types: Optional[List[str]] = None,
                       use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Récupère les événements de tracking pour un utilisateur spécifique.
        
        Args:
            user_id: Identifiant de l'utilisateur
            start_date: Date de début pour les événements (défaut: 30 jours en arrière)
            end_date: Date de fin pour les événements (défaut: maintenant)
            event_types: Types d'événements à récupérer (défaut: tous)
            use_cache: Utiliser le cache si possible
            
        Returns:
            Liste des événements de tracking pour l'utilisateur
        """
        # Définir les dates par défaut si non spécifiées
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=30)
        
        # Formater les dates
        start_str = start_date.isoformat()
        end_str = end_date.isoformat()
        
        # Vérifier si les données sont en cache
        cache_key = f"{user_id}_{start_str}_{end_str}_{'-'.join(event_types or [])}"
        
        if use_cache and cache_key in self.data_cache:
            cache_time = self.cache_timestamp.get(cache_key, 0)
            # Vérifier si le cache est encore valide (moins de 10 minutes)
            if time.time() - cache_time < 600:
                logger.info(f"Using cached tracking data for user {user_id}")
                return self.data_cache[cache_key]
        
        try:
            # Construire la requête
            params = {
                "user_id": user_id,
                "start_date": start_str,
                "end_date": end_str
            }
            
            if event_types:
                params["event_types"] = ",".join(event_types)
            
            headers = {}
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
            
            # Faire la requête avec retry
            events = self._make_request_with_retry(
                endpoint="events",
                params=params,
                headers=headers
            )
            
            if events:
                # Mettre en cache les résultats
                self.data_cache[cache_key] = events
                self.cache_timestamp[cache_key] = time.time()
                
                logger.info(f"Retrieved {len(events)} tracking events for user {user_id}")
                return events
            else:
                logger.warning(f"No tracking events found for user {user_id}")
                return []
            
        except Exception as e:
            logger.error(f"Error retrieving tracking events for user {user_id}: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Si en mode simulation, générer des données simulées
            if self._is_simulation_mode():
                logger.info(f"Using simulated data for user {user_id}")
                return self._generate_simulated_events(user_id, start_date, end_date)
            
            return []
    
    def get_user_sessions(self, user_id: str, start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Récupère les sessions utilisateur avec leurs événements associés.
        
        Args:
            user_id: Identifiant de l'utilisateur
            start_date: Date de début (défaut: 30 jours en arrière)
            end_date: Date de fin (défaut: maintenant)
            
        Returns:
            Liste des sessions utilisateur
        """
        # Récupérer les événements
        events = self.get_user_events(user_id, start_date, end_date)
        
        # Organiser les événements par session
        sessions = {}
        
        for event in events:
            session_id = event.get("session_id")
            if not session_id:
                continue
                
            if session_id not in sessions:
                sessions[session_id] = {
                    "session_id": session_id,
                    "user_id": user_id,
                    "start_time": event.get("timestamp"),
                    "end_time": event.get("timestamp"),
                    "events": []
                }
            
            # Ajouter l'événement à la session
            sessions[session_id]["events"].append(event)
            
            # Mettre à jour les timestamps
            event_time = event.get("timestamp")
            if event_time:
                if event_time < sessions[session_id]["start_time"]:
                    sessions[session_id]["start_time"] = event_time
                if event_time > sessions[session_id]["end_time"]:
                    sessions[session_id]["end_time"] = event_time
        
        # Calculer des statistiques pour chaque session
        for session_id, session in sessions.items():
            events = session["events"]
            session["event_count"] = len(events)
            session["event_types"] = list(set(e.get("event_type") for e in events if e.get("event_type")))
            
            # Calculer la durée si possible
            try:
                start = datetime.fromisoformat(session["start_time"])
                end = datetime.fromisoformat(session["end_time"])
                session["duration_seconds"] = (end - start).total_seconds()
            except (ValueError, TypeError):
                session["duration_seconds"] = None
        
        logger.info(f"Retrieved {len(sessions)} sessions for user {user_id}")
        return list(sessions.values())
    
    def get_aggregate_stats(self, user_id: str, start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Récupère des statistiques agrégées pour un utilisateur.
        
        Args:
            user_id: Identifiant de l'utilisateur
            start_date: Date de début (défaut: 30 jours en arrière)
            end_date: Date de fin (défaut: maintenant)
            
        Returns:
            Statistiques agrégées
        """
        # Récupérer les événements
        events = self.get_user_events(user_id, start_date, end_date)
        
        if not events:
            return {}
        
        # Agréger les statistiques
        stats = {
            "user_id": user_id,
            "total_events": len(events),
            "event_types": {},
            "pages": {},
            "sessions": set()
        }
        
        for event in events:
            # Compter par type d'événement
            event_type = event.get("event_type")
            if event_type:
                if event_type not in stats["event_types"]:
                    stats["event_types"][event_type] = 0
                stats["event_types"][event_type] += 1
            
            # Compter par page
            page = event.get("page")
            if page:
                if page not in stats["pages"]:
                    stats["pages"][page] = 0
                stats["pages"][page] += 1
            
            # Collecter les sessions uniques
            session_id = event.get("session_id")
            if session_id:
                stats["sessions"].add(session_id)
        
        # Convertir l'ensemble de sessions en compte
        stats["unique_sessions"] = len(stats["sessions"])
        del stats["sessions"]
        
        # Calculer des métriques dérivées
        if stats["unique_sessions"] > 0:
            stats["events_per_session"] = stats["total_events"] / stats["unique_sessions"]
        
        logger.info(f"Generated aggregate stats for user {user_id}")
        return stats
    
    def get_real_time_events(self, user_id: str, minutes: int = 30) -> List[Dict[str, Any]]:
        """
        Récupère les événements en temps réel pour un utilisateur.
        
        Args:
            user_id: Identifiant de l'utilisateur
            minutes: Fenêtre temporelle en minutes (par défaut: 30 dernières minutes)
            
        Returns:
            Liste des événements récents
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(minutes=minutes)
        
        # Récupérer les événements récents sans utiliser le cache
        return self.get_user_events(user_id, start_date, end_date, use_cache=False)
    
    def get_user_activity_timeline(self, user_id: str, days: int = 30) -> Dict[str, int]:
        """
        Récupère la timeline d'activité d'un utilisateur sur une période donnée.
        
        Args:
            user_id: Identifiant de l'utilisateur
            days: Nombre de jours à analyser
            
        Returns:
            Dict avec les dates comme clés et le nombre d'événements comme valeurs
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Récupérer les événements
        events = self.get_user_events(user_id, start_date, end_date)
        
        # Initialiser la timeline avec des zéros
        timeline = {}
        current_date = start_date.date()
        while current_date <= end_date.date():
            timeline[current_date.isoformat()] = 0
            current_date += timedelta(days=1)
        
        # Remplir la timeline avec les comptes d'événements
        for event in events:
            try:
                timestamp = event.get("timestamp")
                if timestamp:
                    event_date = datetime.fromisoformat(timestamp).date().isoformat()
                    if event_date in timeline:
                        timeline[event_date] += 1
            except (ValueError, TypeError):
                continue
        
        logger.info(f"Generated activity timeline for user {user_id} over {days} days")
        return timeline
    
    def get_users_with_activity(self, start_date: Optional[datetime] = None,
                              end_date: Optional[datetime] = None,
                              min_events: int = 1) -> List[str]:
        """
        Récupère la liste des utilisateurs actifs pendant une période donnée.
        
        Args:
            start_date: Date de début (défaut: 30 jours en arrière)
            end_date: Date de fin (défaut: maintenant)
            min_events: Nombre minimum d'événements pour considérer un utilisateur comme actif
            
        Returns:
            Liste des IDs d'utilisateurs actifs
        """
        # Définir les dates par défaut si non spécifiées
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=30)
        
        # Formater les dates
        start_str = start_date.isoformat()
        end_str = end_date.isoformat()
        
        try:
            # Construire la requête
            params = {
                "start_date": start_str,
                "end_date": end_str,
                "min_events": min_events
            }
            
            headers = {}
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
            
            # Faire la requête avec retry
            active_users = self._make_request_with_retry(
                endpoint="active_users",
                params=params,
                headers=headers
            )
            
            if active_users:
                logger.info(f"Retrieved {len(active_users)} active users")
                return active_users
            else:
                logger.warning("No active users found")
                return []
            
        except Exception as e:
            logger.error(f"Error retrieving active users: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Si en mode simulation, générer des utilisateurs simulés
            if self._is_simulation_mode():
                logger.info("Using simulated active users")
                return [f"user_{i}" for i in range(1, 21)]
            
            return []
    
    def register_profile_update(self, user_id: str, update_type: str, timestamp: Optional[datetime] = None) -> bool:
        """
        Enregistre une mise à jour de profil dans le système de tracking.
        
        Args:
            user_id: Identifiant de l'utilisateur
            update_type: Type de mise à jour (features, preferences, etc.)
            timestamp: Horodatage de la mise à jour (défaut: maintenant)
            
        Returns:
            Booléen indiquant si l'enregistrement a réussi
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        try:
            # Construire les données à envoyer
            data = {
                "user_id": user_id,
                "event_type": "profile_update",
                "timestamp": timestamp.isoformat(),
                "properties": {
                    "update_type": update_type
                }
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
            
            # Faire la requête avec retry
            result = self._make_request_with_retry(
                endpoint="record",
                method="POST",
                data=json.dumps(data),
                headers=headers
            )
            
            success = result and result.get("success") == True
            if success:
                logger.info(f"Successfully registered profile update for user {user_id}")
            else:
                logger.warning(f"Failed to register profile update for user {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error registering profile update for user {user_id}: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    def _make_request_with_retry(self, endpoint: str, method: str = "GET", params: Dict[str, Any] = None, 
                               data: str = None, headers: Dict[str, str] = None) -> Any:
        """
        Effectue une requête HTTP avec mécanisme de retry.
        
        Args:
            endpoint: Point de terminaison de l'API
            method: Méthode HTTP (GET, POST, etc.)
            params: Paramètres de requête
            data: Données à envoyer (pour POST/PUT)
            headers: En-têtes HTTP
            
        Returns:
            Données de réponse (JSON)
        """
        url = f"{self.tracking_url}/{endpoint}"
        retry_count = 0
        
        while retry_count < self.max_retries:
            try:
                if method.upper() == "GET":
                    response = requests.get(
                        url,
                        params=params,
                        headers=headers,
                        timeout=self.timeout
                    )
                elif method.upper() == "POST":
                    response = requests.post(
                        url,
                        params=params,
                        data=data,
                        headers=headers,
                        timeout=self.timeout
                    )
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                return response.json()
                
            except requests.RequestException as e:
                retry_count += 1
                logger.warning(f"Request failed (attempt {retry_count}/{self.max_retries}): {str(e)}")
                
                if retry_count >= self.max_retries:
                    raise
                
                time.sleep(self.retry_delay)
    
    def _is_simulation_mode(self) -> bool:
        """
        Vérifie si le module fonctionne en mode simulation.
        
        Returns:
            True si en mode simulation, False sinon
        """
        # Vérifier si le mode simulation est activé dans la config ou si l'URL est localhost
        return self.tracking_url.startswith(("http://localhost", "http://127.0.0.1")) or "simulation" in self.tracking_url.lower()
    
    def _generate_simulated_events(self, user_id: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Génère des événements de tracking simulés pour le développement.
        
        Args:
            user_id: Identifiant de l'utilisateur
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Liste des événements simulés
        """
        import random
        from datetime import timedelta
        
        events = []
        event_types = ["page_view", "click", "search", "filter", "download", "apply"]
        pages = ["/jobs", "/profile", "/dashboard", "/search", "/recommendations"]
        
        # Générer des dates aléatoires dans la plage
        total_seconds = int((end_date - start_date).total_seconds())
        event_count = random.randint(50, 200)  # Nombre d'événements à générer
        
        for _ in range(event_count):
            # Générer un timestamp aléatoire dans la plage
            random_seconds = random.randint(0, total_seconds)
            timestamp = start_date + timedelta(seconds=random_seconds)
            
            # Générer une session (la même pour des événements proches dans le temps)
            session_id = f"session_{random.randint(1, 5)}"
            
            # Générer l'événement
            event_type = random.choice(event_types)
            page = random.choice(pages)
            
            event = {
                "user_id": user_id,
                "timestamp": timestamp.isoformat(),
                "event_type": event_type,
                "session_id": session_id,
                "page": page,
                "properties": {}
            }
            
            # Ajouter des propriétés spécifiques selon le type d'événement
            if event_type == "click":
                event["properties"]["element_id"] = f"element_{random.randint(1, 20)}"
                event["properties"]["element_type"] = random.choice(["button", "link", "card"])
                
            elif event_type == "search":
                event["properties"]["query"] = random.choice(["java developer", "marketing manager", "data scientist"])
                event["properties"]["results_count"] = random.randint(0, 50)
                
            elif event_type == "filter":
                filter_types = ["category", "location", "salary", "experience"]
                filter_type = random.choice(filter_types)
                event["properties"]["filter_type"] = filter_type
                
                if filter_type == "category":
                    event["properties"]["filter_value"] = random.choice(["IT", "Marketing", "Sales"])
                elif filter_type == "location":
                    event["properties"]["filter_value"] = random.choice(["Paris", "Lyon", "Marseille"])
                elif filter_type == "salary":
                    event["properties"]["filter_value"] = random.choice(["<30k", "30-60k", ">60k"])
                else:
                    event["properties"]["filter_value"] = random.choice(["Junior", "Intermediate", "Senior"])
            
            events.append(event)
        
        # Trier par timestamp
        events.sort(key=lambda x: x["timestamp"])
        
        logger.info(f"Generated {len(events)} simulated events for user {user_id}")
        return events
