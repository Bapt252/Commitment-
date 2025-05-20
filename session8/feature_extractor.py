"""
Module d'extraction de caractéristiques comportementales.

Ce module est responsable de l'extraction des caractéristiques comportementales
à partir des données de tracking des utilisateurs. Ces caractéristiques servent ensuite
à établir le profil comportemental de l'utilisateur.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Any, Optional, Tuple

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class FeatureExtractor:
    """
    Extracteur de caractéristiques comportementales à partir des données de tracking.
    """
    
    def __init__(self, db_connector=None):
        """
        Initialise l'extracteur de caractéristiques.
        
        Args:
            db_connector: Connecteur vers la base de données de tracking
        """
        self.db_connector = db_connector
        self.feature_definitions = {
            "engagement_score": self._calculate_engagement_score,
            "session_duration": self._calculate_session_duration,
            "active_days": self._calculate_active_days,
            "click_frequency": self._calculate_click_frequency,
            "search_depth": self._calculate_search_depth,
            "content_preference": self._extract_content_preference,
            "interaction_patterns": self._extract_interaction_patterns
        }
        logger.info("FeatureExtractor initialized")
        
    def extract_features(self, user_id: str, start_date: Optional[datetime] = None, 
                         end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Extrait les caractéristiques comportementales pour un utilisateur spécifique.
        
        Args:
            user_id: Identifiant de l'utilisateur
            start_date: Date de début pour l'extraction (par défaut: 30 jours en arrière)
            end_date: Date de fin pour l'extraction (par défaut: maintenant)
            
        Returns:
            Dict contenant les caractéristiques extraites
        """
        logger.info(f"Extracting features for user {user_id}")
        
        # Définir les dates par défaut si non spécifiées
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=30)
            
        # Récupérer les données de tracking
        raw_data = self._get_tracking_data(user_id, start_date, end_date)
        
        if not raw_data or len(raw_data) == 0:
            logger.warning(f"No tracking data found for user {user_id}")
            return {}
        
        # Extraire les différentes caractéristiques
        features = {}
        for feature_name, feature_extractor in self.feature_definitions.items():
            try:
                features[feature_name] = feature_extractor(raw_data, user_id, start_date, end_date)
            except Exception as e:
                logger.error(f"Error extracting feature {feature_name}: {str(e)}")
                features[feature_name] = None
                
        # Ajouter des métadonnées sur l'extraction
        features["extraction_date"] = datetime.now().isoformat()
        features["data_start_date"] = start_date.isoformat()
        features["data_end_date"] = end_date.isoformat()
        features["user_id"] = user_id
        
        logger.info(f"Extracted {len(features)} features for user {user_id}")
        return features
    
    def _get_tracking_data(self, user_id: str, start_date: datetime, 
                          end_date: datetime) -> List[Dict[str, Any]]:
        """
        Récupère les données de tracking pour un utilisateur dans une période donnée.
        
        Args:
            user_id: Identifiant de l'utilisateur
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Liste des événements de tracking
        """
        # Si un connecteur DB est disponible, utiliser celui-ci
        if self.db_connector:
            try:
                query = f"""
                SELECT * FROM tracking_events 
                WHERE user_id = '{user_id}' 
                AND timestamp BETWEEN '{start_date.isoformat()}' AND '{end_date.isoformat()}'
                ORDER BY timestamp ASC
                """
                return self.db_connector.execute_query(query)
            except Exception as e:
                logger.error(f"Error retrieving tracking data: {str(e)}")
                return []
        
        # Sinon, utiliser des données simulées pour le développement
        return self._generate_mock_tracking_data(user_id, start_date, end_date)
    
    def _generate_mock_tracking_data(self, user_id: str, start_date: datetime, 
                                    end_date: datetime) -> List[Dict[str, Any]]:
        """
        Génère des données de tracking simulées pour le développement.
        
        Args:
            user_id: Identifiant de l'utilisateur
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Liste des événements de tracking simulés
        """
        logger.info(f"Generating mock tracking data for user {user_id}")
        
        # Calculer le nombre de jours entre les dates
        days_diff = (end_date - start_date).days
        if days_diff <= 0:
            days_diff = 1
        
        # Générer des données simulées
        mock_data = []
        event_types = ["page_view", "click", "search", "filter", "download", "apply"]
        
        # Simuler des jours actifs aléatoires
        active_days = np.random.choice(range(days_diff), size=min(days_diff, 20), replace=False)
        
        for day_offset in active_days:
            # Nombre d'événements par jour actif
            events_count = np.random.randint(5, 50)
            base_date = start_date + timedelta(days=day_offset)
            
            for _ in range(events_count):
                event_time = base_date + timedelta(seconds=np.random.randint(0, 86400))
                event_type = np.random.choice(event_types, p=[0.4, 0.3, 0.1, 0.1, 0.05, 0.05])
                
                event = {
                    "user_id": user_id,
                    "timestamp": event_time.isoformat(),
                    "event_type": event_type,
                    "session_id": f"session_{day_offset}_{np.random.randint(1, 4)}",
                    "page": f"/page/{np.random.randint(1, 20)}",
                    "properties": {}
                }
                
                # Ajouter des propriétés spécifiques selon le type d'événement
                if event_type == "click":
                    event["properties"]["element_id"] = f"element_{np.random.randint(1, 100)}"
                    event["properties"]["element_type"] = np.random.choice(["button", "link", "card"])
                elif event_type == "search":
                    event["properties"]["query"] = f"query_{np.random.randint(1, 10)}"
                    event["properties"]["results_count"] = np.random.randint(0, 50)
                elif event_type == "filter":
                    event["properties"]["filter_type"] = np.random.choice(["date", "location", "salary", "skills"])
                    event["properties"]["filter_value"] = f"value_{np.random.randint(1, 10)}"
                elif event_type == "download":
                    event["properties"]["document_id"] = f"doc_{np.random.randint(1, 100)}"
                    event["properties"]["document_type"] = np.random.choice(["cv", "job", "report"])
                elif event_type == "apply":
                    event["properties"]["job_id"] = f"job_{np.random.randint(1, 100)}"
                    event["properties"]["application_method"] = np.random.choice(["direct", "email", "form"])
                
                mock_data.append(event)
        
        # Trier par timestamp
        mock_data.sort(key=lambda x: x["timestamp"])
        logger.info(f"Generated {len(mock_data)} mock events for user {user_id}")
        
        return mock_data
    
    def _calculate_engagement_score(self, data: List[Dict[str, Any]], user_id: str, 
                                   start_date: datetime, end_date: datetime) -> float:
        """
        Calcule un score d'engagement basé sur la fréquence et la variété des interactions.
        
        Args:
            data: Données de tracking
            user_id: Identifiant de l'utilisateur
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Score d'engagement entre 0 et 100
        """
        if not data:
            return 0.0
        
        # Paramètres pour le calcul du score
        weights = {
            "page_view": 1,
            "click": 2,
            "search": 3,
            "filter": 2,
            "download": 5,
            "apply": 10
        }
        
        # Calculer le score pondéré des événements
        total_score = 0
        for event in data:
            event_type = event.get("event_type", "page_view")
            weight = weights.get(event_type, 1)
            total_score += weight
        
        # Normaliser le score (max théorique: 50 événements * poids moyen de 3 = 150)
        normalized_score = min(100, total_score / 1.5)
        
        return normalized_score
    
    def _calculate_session_duration(self, data: List[Dict[str, Any]], user_id: str, 
                                   start_date: datetime, end_date: datetime) -> Dict[str, float]:
        """
        Calcule la durée moyenne des sessions pour un utilisateur.
        
        Args:
            data: Données de tracking
            user_id: Identifiant de l'utilisateur
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Dict contenant les statistiques de durée des sessions
        """
        if not data:
            return {"avg_duration_seconds": 0, "total_sessions": 0, "max_duration_seconds": 0}
        
        # Grouper les événements par session
        sessions = {}
        for event in data:
            session_id = event.get("session_id", "unknown")
            timestamp = datetime.fromisoformat(event["timestamp"])
            
            if session_id not in sessions:
                sessions[session_id] = {"start": timestamp, "end": timestamp}
            else:
                if timestamp < sessions[session_id]["start"]:
                    sessions[session_id]["start"] = timestamp
                if timestamp > sessions[session_id]["end"]:
                    sessions[session_id]["end"] = timestamp
        
        # Calculer les durées des sessions
        durations = []
        for session in sessions.values():
            duration = (session["end"] - session["start"]).total_seconds()
            # Ignorer les sessions trop courtes (moins de 10 secondes)
            if duration >= 10:
                durations.append(duration)
        
        if not durations:
            return {"avg_duration_seconds": 0, "total_sessions": 0, "max_duration_seconds": 0}
        
        return {
            "avg_duration_seconds": np.mean(durations),
            "total_sessions": len(durations),
            "max_duration_seconds": max(durations)
        }
    
    def _calculate_active_days(self, data: List[Dict[str, Any]], user_id: str, 
                              start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Calcule le nombre de jours actifs et la distribution d'activité.
        
        Args:
            data: Données de tracking
            user_id: Identifiant de l'utilisateur
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Dict contenant les statistiques de jours actifs
        """
        if not data:
            return {"active_days_count": 0, "activity_ratio": 0}
        
        # Extraire les dates uniques des événements
        dates = set()
        for event in data:
            date_str = event["timestamp"].split("T")[0]
            dates.add(date_str)
        
        # Calculer le nombre total de jours dans la période
        total_days = (end_date - start_date).days + 1
        
        return {
            "active_days_count": len(dates),
            "activity_ratio": len(dates) / total_days if total_days > 0 else 0,
            "daily_distribution": self._calculate_daily_distribution(data)
        }
    
    def _calculate_daily_distribution(self, data: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Calcule la distribution des événements par jour de la semaine.
        
        Args:
            data: Données de tracking
            
        Returns:
            Dict contenant le nombre d'événements par jour de la semaine
        """
        days = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 
                4: "Friday", 5: "Saturday", 6: "Sunday"}
        
        distribution = {day: 0 for day in days.values()}
        
        for event in data:
            date = datetime.fromisoformat(event["timestamp"])
            day_name = days[date.weekday()]
            distribution[day_name] += 1
        
        return distribution
    
    def _calculate_click_frequency(self, data: List[Dict[str, Any]], user_id: str, 
                                  start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Calcule la fréquence et les types de clics.
        
        Args:
            data: Données de tracking
            user_id: Identifiant de l'utilisateur
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Dict contenant les statistiques de clics
        """
        clicks = [event for event in data if event.get("event_type") == "click"]
        
        if not clicks:
            return {"click_count": 0, "clicks_per_session": 0}
        
        # Grouper les clics par session
        session_clicks = {}
        for click in clicks:
            session_id = click.get("session_id", "unknown")
            if session_id not in session_clicks:
                session_clicks[session_id] = []
            session_clicks[session_id].append(click)
        
        # Calculer les statistiques de clics
        element_types = {}
        for click in clicks:
            element_type = click.get("properties", {}).get("element_type", "unknown")
            if element_type not in element_types:
                element_types[element_type] = 0
            element_types[element_type] += 1
        
        return {
            "click_count": len(clicks),
            "clicks_per_session": len(clicks) / len(session_clicks) if session_clicks else 0,
            "element_type_distribution": element_types
        }
    
    def _calculate_search_depth(self, data: List[Dict[str, Any]], user_id: str, 
                              start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Analyse le comportement de recherche et la profondeur d'exploration.
        
        Args:
            data: Données de tracking
            user_id: Identifiant de l'utilisateur
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Dict contenant les statistiques de recherche
        """
        searches = [event for event in data if event.get("event_type") == "search"]
        
        if not searches:
            return {"search_count": 0, "avg_results_viewed": 0}
        
        # Extraire les requêtes uniques
        unique_queries = set()
        results_counts = []
        
        for search in searches:
            props = search.get("properties", {})
            query = props.get("query", "")
            if query:
                unique_queries.add(query)
            
            results_count = props.get("results_count", 0)
            if results_count:
                results_counts.append(results_count)
        
        return {
            "search_count": len(searches),
            "unique_queries_count": len(unique_queries),
            "avg_results_count": np.mean(results_counts) if results_counts else 0
        }
    
    def _extract_content_preference(self, data: List[Dict[str, Any]], user_id: str, 
                                  start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Extrait les préférences de contenu basées sur les interactions.
        
        Args:
            data: Données de tracking
            user_id: Identifiant de l'utilisateur
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Dict contenant les préférences de contenu
        """
        # Analyser les téléchargements
        downloads = [event for event in data if event.get("event_type") == "download"]
        download_types = {}
        
        for download in downloads:
            doc_type = download.get("properties", {}).get("document_type", "unknown")
            if doc_type not in download_types:
                download_types[doc_type] = 0
            download_types[doc_type] += 1
        
        # Analyser les postulations
        applications = [event for event in data if event.get("event_type") == "apply"]
        application_methods = {}
        
        for application in applications:
            method = application.get("properties", {}).get("application_method", "unknown")
            if method not in application_methods:
                application_methods[method] = 0
            application_methods[method] += 1
        
        return {
            "download_preferences": download_types,
            "application_preferences": application_methods,
            "downloads_count": len(downloads),
            "applications_count": len(applications)
        }
    
    def _extract_interaction_patterns(self, data: List[Dict[str, Any]], user_id: str, 
                                     start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Détecte des patterns dans les séquences d'interactions.
        
        Args:
            data: Données de tracking
            user_id: Identifiant de l'utilisateur
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Dict contenant les patterns d'interaction détectés
        """
        if not data or len(data) < 3:
            return {"common_sequences": [], "event_type_distribution": {}}
        
        # Calculer la distribution des types d'événements
        event_types = {}
        for event in data:
            event_type = event.get("event_type", "unknown")
            if event_type not in event_types:
                event_types[event_type] = 0
            event_types[event_type] += 1
        
        # Détecter les séquences communes (séquences de 3 événements)
        sequences = {}
        for i in range(len(data) - 2):
            seq = tuple(data[i+j].get("event_type", "unknown") for j in range(3))
            if seq not in sequences:
                sequences[seq] = 0
            sequences[seq] += 1
        
        # Trier les séquences par fréquence
        sorted_sequences = sorted(sequences.items(), key=lambda x: x[1], reverse=True)
        top_sequences = sorted_sequences[:5] if sorted_sequences else []
        
        formatted_sequences = [
            {"sequence": list(seq), "count": count}
            for seq, count in top_sequences
        ]
        
        return {
            "common_sequences": formatted_sequences,
            "event_type_distribution": event_types
        }
