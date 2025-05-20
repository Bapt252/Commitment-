"""
Module d'intégration avec le système de tracking existant.

Ce module permet d'intégrer le système de profilage utilisateur avec le système
de tracking existant pour récupérer les événements et mettre à jour les profils.
"""

import requests
import json
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import os
import threading

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class TrackingIntegration:
    """
    Intégration avec le système de tracking existant pour la collecte des données comportementales.
    """
    
    def __init__(self, profile_manager=None, feature_extractor=None, pattern_detector=None, 
                 preference_calculator=None, user_clustering=None, config=None):
        """
        Initialise l'intégration avec le système de tracking.
        
        Args:
            profile_manager: Gestionnaire de profils utilisateurs
            feature_extractor: Extracteur de caractéristiques comportementales
            pattern_detector: Détecteur de patterns comportementaux
            preference_calculator: Calculateur de préférences
            user_clustering: Module de clustering d'utilisateurs
            config: Configuration de l'intégration
        """
        self.profile_manager = profile_manager
        self.feature_extractor = feature_extractor
        self.pattern_detector = pattern_detector
        self.preference_calculator = preference_calculator
        self.user_clustering = user_clustering
        
        # Configuration par défaut
        self.config = {
            "tracking_service_url": "http://localhost:8080/api/tracking",
            "auth_token": "",
            "batch_size": 100,
            "timeout_seconds": 30,
            "max_retries": 3,
            "retry_delay_seconds": 5,
            "polling_interval_seconds": 300,  # 5 minutes
            "auto_processing_enabled": True,
            "events_cache_path": "./data/session8/tracking_cache",
            "events_cache_enabled": True
        }
        
        # Mise à jour de la configuration si fournie
        if config:
            self.config.update(config)
        
        # S'assurer que le chemin de cache existe
        if self.config["events_cache_enabled"]:
            os.makedirs(self.config["events_cache_path"], exist_ok=True)
        
        # État de l'intégration
        self.running = False
        self.polling_thread = None
        self.last_processed_timestamp = datetime.now() - timedelta(days=1)
        
        # Démarrer le traitement automatique si activé
        if self.config["auto_processing_enabled"]:
            self.start_auto_processing()
        
        logger.info("TrackingIntegration initialized")
    
    def fetch_events(self, start_time: datetime, end_time: Optional[datetime] = None,
                    event_types: Optional[List[str]] = None,
                    user_ids: Optional[List[str]] = None,
                    limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Récupère les événements de tracking depuis le service de tracking.
        
        Args:
            start_time: Timestamp de début pour la récupération des événements
            end_time: Timestamp de fin (par défaut: maintenant)
            event_types: Liste des types d'événements à récupérer (par défaut: tous)
            user_ids: Liste des identifiants d'utilisateurs (par défaut: tous)
            limit: Nombre maximum d'événements à récupérer
            
        Returns:
            Liste des événements de tracking
        """
        if end_time is None:
            end_time = datetime.now()
        
        # Préparer les paramètres de requête
        params = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "limit": limit
        }
        
        if event_types:
            params["event_types"] = ",".join(event_types)
        
        if user_ids:
            params["user_ids"] = ",".join(user_ids)
        
        # Préparer les headers
        headers = {"Content-Type": "application/json"}
        if self.config["auth_token"]:
            headers["Authorization"] = f"Bearer {self.config['auth_token']}"
        
        # Cache key pour les résultats
        cache_key = f"{start_time.isoformat()}-{end_time.isoformat()}"
        if event_types:
            cache_key += f"-{','.join(event_types)}"
        if user_ids:
            cache_key += f"-{','.join(user_ids)}"
        cache_key += f"-{limit}"
        
        # Vérifier le cache
        if self.config["events_cache_enabled"]:
            cached_events = self._load_from_cache(cache_key)
            if cached_events:
                logger.info(f"Retrieved {len(cached_events)} events from cache")
                return cached_events
        
        # Effectuer la requête avec retry
        events = []
        retry_count = 0
        
        while retry_count < self.config["max_retries"]:
            try:
                response = requests.get(
                    f"{self.config['tracking_service_url']}/events",
                    params=params,
                    headers=headers,
                    timeout=self.config["timeout_seconds"]
                )
                
                if response.status_code == 200:
                    events = response.json().get("events", [])
                    logger.info(f"Fetched {len(events)} tracking events")
                    
                    # Sauvegarder dans le cache
                    if self.config["events_cache_enabled"] and events:
                        self._save_to_cache(cache_key, events)
                    
                    return events
                else:
                    logger.error(f"Failed to fetch events: {response.status_code} - {response.text}")
            except requests.RequestException as e:
                logger.error(f"Request error fetching events: {str(e)}")
            
            # Attendre avant de réessayer
            retry_count += 1
            if retry_count < self.config["max_retries"]:
                logger.info(f"Retrying in {self.config['retry_delay_seconds']} seconds (attempt {retry_count+1}/{self.config['max_retries']})")
                time.sleep(self.config["retry_delay_seconds"])
        
        # Si on arrive ici, toutes les tentatives ont échoué
        logger.error(f"Failed to fetch events after {self.config['max_retries']} retries")
        
        # Si le service de tracking est indisponible, générer des données simulées
        logger.warning("Generating mock data since tracking service is unavailable")
        return self._generate_mock_tracking_data(start_time, end_time, user_ids, limit)
    
    def process_events(self, events: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Traite les événements de tracking pour mettre à jour les profils et les statistiques.
        
        Args:
            events: Liste des événements de tracking à traiter
            
        Returns:
            Dict contenant des statistiques sur le traitement
        """
        if not events:
            logger.info("No events to process")
            return {"processed": 0, "profiles_updated": 0, "patterns_updated": 0, "preferences_updated": 0}
        
        logger.info(f"Processing {len(events)} tracking events")
        
        # Grouper les événements par utilisateur
        user_events = {}
        for event in events:
            user_id = event.get("user_id")
            if not user_id:
                continue
            
            if user_id not in user_events:
                user_events[user_id] = []
            
            user_events[user_id].append(event)
        
        # Traiter les événements pour chaque utilisateur
        processed_count = 0
        profiles_updated = 0
        patterns_updated = 0
        preferences_updated = 0
        
        for user_id, user_event_list in user_events.items():
            processed_count += len(user_event_list)
            
            # Extraire les caractéristiques et mettre à jour le profil
            if self.feature_extractor and self.profile_manager:
                try:
                    features = self.feature_extractor.extract_features(user_id)
                    if features:
                        self.profile_manager.update_profile(user_id, {"features": features})
                        profiles_updated += 1
                except Exception as e:
                    logger.error(f"Error updating profile for user {user_id}: {str(e)}")
            
            # Analyser les patterns comportementaux
            if self.pattern_detector:
                try:
                    patterns = self.pattern_detector.analyze_user_patterns(user_id)
                    if patterns:
                        patterns_updated += 1
                except Exception as e:
                    logger.error(f"Error analyzing patterns for user {user_id}: {str(e)}")
            
            # Calculer les préférences
            if self.preference_calculator:
                try:
                    preferences = self.preference_calculator.calculate_preferences(user_id)
                    if preferences:
                        preferences_updated += 1
                except Exception as e:
                    logger.error(f"Error calculating preferences for user {user_id}: {str(e)}")
        
        # Mettre à jour le clustering après avoir traité tous les utilisateurs
        if self.user_clustering and profiles_updated > 0:
            try:
                self.user_clustering.update_clusters()
                logger.info("User clusters updated")
            except Exception as e:
                logger.error(f"Error updating user clusters: {str(e)}")
        
        logger.info(f"Processed {processed_count} events, updated {profiles_updated} profiles, {patterns_updated} patterns, {preferences_updated} preferences")
        
        return {
            "processed": processed_count,
            "profiles_updated": profiles_updated,
            "patterns_updated": patterns_updated,
            "preferences_updated": preferences_updated
        }
    
    def process_recent_events(self) -> Dict[str, int]:
        """
        Récupère et traite les événements récents depuis le dernier traitement.
        
        Returns:
            Dict contenant des statistiques sur le traitement
        """
        now = datetime.now()
        start_time = self.last_processed_timestamp
        
        logger.info(f"Processing events from {start_time} to {now}")
        
        # Récupérer les événements récents
        events = self.fetch_events(start_time, now)
        
        # Mettre à jour le timestamp du dernier traitement
        self.last_processed_timestamp = now
        
        # Traiter les événements
        return self.process_events(events)
    
    def start_auto_processing(self):
        """Démarre le traitement automatique des événements en arrière-plan."""
        if self.running:
            logger.warning("Auto-processing already running")
            return
        
        self.running = True
        self.polling_thread = threading.Thread(target=self._auto_processing_loop)
        self.polling_thread.daemon = True
        self.polling_thread.start()
        
        logger.info(f"Started auto-processing with polling interval of {self.config['polling_interval_seconds']} seconds")
    
    def stop_auto_processing(self):
        """Arrête le traitement automatique des événements."""
        self.running = False
        if self.polling_thread:
            self.polling_thread.join(timeout=10)
            logger.info("Stopped auto-processing")
    
    def _auto_processing_loop(self):
        """Boucle de traitement automatique des événements."""
        while self.running:
            try:
                self.process_recent_events()
            except Exception as e:
                logger.error(f"Error in auto-processing loop: {str(e)}")
            
            # Attendre l'intervalle de polling
            for _ in range(self.config["polling_interval_seconds"]):
                if not self.running:
                    break
                time.sleep(1)
    
    def _save_to_cache(self, key: str, events: List[Dict[str, Any]]) -> bool:
        """
        Sauvegarde les événements dans le cache.
        
        Args:
            key: Clé de cache
            events: Liste des événements à sauvegarder
            
        Returns:
            True si la sauvegarde a réussi, False sinon
        """
        if not self.config["events_cache_enabled"]:
            return False
        
        # Sécuriser la clé pour l'utiliser comme nom de fichier
        import hashlib
        safe_key = hashlib.md5(key.encode()).hexdigest()
        cache_file = os.path.join(self.config["events_cache_path"], f"{safe_key}.json")
        
        try:
            with open(cache_file, "w") as f:
                json.dump({
                    "key": key,
                    "timestamp": datetime.now().isoformat(),
                    "events": events
                }, f)
            return True
        except Exception as e:
            logger.error(f"Failed to save to cache: {str(e)}")
            return False
    
    def _load_from_cache(self, key: str) -> Optional[List[Dict[str, Any]]]:
        """
        Charge les événements depuis le cache.
        
        Args:
            key: Clé de cache
            
        Returns:
            Liste des événements ou None si pas trouvés
        """
        if not self.config["events_cache_enabled"]:
            return None
        
        # Sécuriser la clé pour l'utiliser comme nom de fichier
        import hashlib
        safe_key = hashlib.md5(key.encode()).hexdigest()
        cache_file = os.path.join(self.config["events_cache_path"], f"{safe_key}.json")
        
        if not os.path.exists(cache_file):
            return None
        
        try:
            with open(cache_file, "r") as f:
                cache_data = json.load(f)
                
                # Vérifier que c'est bien la bonne clé
                if cache_data.get("key") != key:
                    return None
                
                # Vérifier que le cache n'est pas trop ancien (1 heure max)
                cache_time = datetime.fromisoformat(cache_data.get("timestamp"))
                if datetime.now() - cache_time > timedelta(hours=1):
                    return None
                
                return cache_data.get("events", [])
        except Exception as e:
            logger.error(f"Failed to load from cache: {str(e)}")
            return None
    
    def track_event(self, user_id: str, event_type: str, properties: Dict[str, Any] = None) -> bool:
        """
        Envoie un événement au système de tracking.
        
        Args:
            user_id: Identifiant de l'utilisateur
            event_type: Type d'événement
            properties: Propriétés de l'événement
            
        Returns:
            True si l'événement a été envoyé avec succès, False sinon
        """
        if not properties:
            properties = {}
        
        # Préparer l'événement
        event = {
            "user_id": user_id,
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "properties": properties
        }
        
        # Préparer les headers
        headers = {"Content-Type": "application/json"}
        if self.config["auth_token"]:
            headers["Authorization"] = f"Bearer {self.config['auth_token']}"
        
        # Envoyer l'événement avec retry
        retry_count = 0
        
        while retry_count < self.config["max_retries"]:
            try:
                response = requests.post(
                    f"{self.config['tracking_service_url']}/events",
                    json=event,
                    headers=headers,
                    timeout=self.config["timeout_seconds"]
                )
                
                if response.status_code in (200, 201, 202):
                    logger.info(f"Tracked event {event_type} for user {user_id}")
                    return True
                else:
                    logger.error(f"Failed to track event: {response.status_code} - {response.text}")
            except requests.RequestException as e:
                logger.error(f"Request error tracking event: {str(e)}")
            
            # Attendre avant de réessayer
            retry_count += 1
            if retry_count < self.config["max_retries"]:
                logger.info(f"Retrying in {self.config['retry_delay_seconds']} seconds (attempt {retry_count+1}/{self.config['max_retries']})")
                time.sleep(self.config["retry_delay_seconds"])
        
        # Si on arrive ici, toutes les tentatives ont échoué
        logger.error(f"Failed to track event after {self.config['max_retries']} retries")
        return False
    
    def _generate_mock_tracking_data(self, start_time: datetime, end_time: datetime, 
                                   user_ids: Optional[List[str]] = None, 
                                   limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Génère des données de tracking simulées pour le développement.
        
        Args:
            start_time: Timestamp de début
            end_time: Timestamp de fin
            user_ids: Liste des identifiants d'utilisateurs (génère des IDs aléatoires si None)
            limit: Nombre maximum d'événements à générer
            
        Returns:
            Liste des événements simulés
        """
        import random
        from datetime import datetime, timedelta
        
        logger.info(f"Generating mock tracking data from {start_time} to {end_time}")
        
        # Si pas d'utilisateurs spécifiés, en générer quelques-uns
        if not user_ids:
            user_ids = [f"user_{i}" for i in range(1, 11)]
        
        # Types d'événements possibles
        event_types = ["page_view", "click", "search", "filter", "download", "apply"]
        
        # Générer des événements aléatoires
        events = []
        for _ in range(min(limit, 1000)):  # Limiter à 1000 événements max
            user_id = random.choice(user_ids)
            event_type = random.choice(event_types)
            
            # Timestamp aléatoire dans la plage spécifiée
            time_range = (end_time - start_time).total_seconds()
            random_seconds = random.randint(0, int(time_range))
            timestamp = start_time + timedelta(seconds=random_seconds)
            
            # Générer des propriétés selon le type d'événement
            properties = {}
            
            if event_type == "page_view":
                pages = ["/home", "/jobs", "/profile", "/candidates", "/settings", "/stats"]
                properties["page"] = random.choice(pages)
                properties["referrer"] = random.choice(["direct", "search", "social", "email"])
            
            elif event_type == "click":
                elements = ["button", "link", "card", "tab", "input", "dropdown"]
                properties["element_type"] = random.choice(elements)
                properties["element_id"] = f"el_{random.randint(1, 100)}"
                properties["page"] = f"/page_{random.randint(1, 10)}"
            
            elif event_type == "search":
                queries = ["python developer", "data scientist", "project manager", "UI designer", "sales manager"]
                properties["query"] = random.choice(queries)
                properties["results_count"] = random.randint(0, 50)
                properties["page"] = 1
            
            elif event_type == "filter":
                filter_types = ["location", "salary", "experience", "skills", "job_type"]
                filter_type = random.choice(filter_types)
                properties["filter_type"] = filter_type
                
                if filter_type == "location":
                    locations = ["paris", "lyon", "marseille", "bordeaux", "toulouse"]
                    properties["filter_value"] = random.choice(locations)
                elif filter_type == "salary":
                    properties["filter_value"] = f"{random.randint(30, 120)}k-{random.randint(45, 150)}k"
                elif filter_type == "experience":
                    properties["filter_value"] = random.choice(["entry", "mid", "senior", "lead", "executive"])
                elif filter_type == "skills":
                    skills = ["python", "javascript", "react", "data analysis", "product management"]
                    properties["filter_value"] = random.choice(skills)
                elif filter_type == "job_type":
                    properties["filter_value"] = random.choice(["full-time", "part-time", "contract", "remote"])
            
            elif event_type == "download":
                doc_types = ["cv", "job_description", "report", "company_profile"]
                properties["document_type"] = random.choice(doc_types)
                properties["document_id"] = f"doc_{random.randint(1, 100)}"
            
            elif event_type == "apply":
                properties["job_id"] = f"job_{random.randint(1, 100)}"
                properties["application_method"] = random.choice(["direct", "email", "form"])
                
                # Ajouter des métadonnées pour les offres d'emploi
                categories = ["engineering", "marketing", "sales", "design", "finance"]
                locations = ["paris", "lyon", "marseille", "bordeaux", "toulouse"]
                properties["job_category"] = random.choice(categories)
                properties["job_location"] = random.choice(locations)
            
            # Ajouter l'événement à la liste
            events.append({
                "user_id": user_id,
                "event_type": event_type,
                "timestamp": timestamp.isoformat(),
                "properties": properties,
                "session_id": f"session_{random.randint(1, 10)}_{user_id}"
            })
        
        # Trier les événements par timestamp
        events.sort(key=lambda x: x["timestamp"])
        
        logger.info(f"Generated {len(events)} mock tracking events")
        return events
