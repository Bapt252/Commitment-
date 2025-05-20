"""
Module de détection de patterns comportementaux.

Ce module est responsable de la détection de patterns récurrents dans le
comportement des utilisateurs à partir des données de tracking.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Any, Optional, Tuple
import json
import os
from collections import Counter, defaultdict
import networkx as nx
from itertools import combinations

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class PatternDetector:
    """
    Module de détection de patterns comportementaux dans les données de tracking.
    """
    
    def __init__(self, db_connector=None, storage_path: str = "./patterns"):
        """
        Initialise le détecteur de patterns.
        
        Args:
            db_connector: Connecteur vers la base de données de tracking
            storage_path: Chemin vers le dossier de stockage des patterns
        """
        self.db_connector = db_connector
        self.storage_path = storage_path
        
        # Créer le dossier de stockage s'il n'existe pas
        os.makedirs(storage_path, exist_ok=True)
        
        # Liste des types de patterns à détecter
        self.pattern_types = {
            "sequence_patterns": self._detect_sequence_patterns,
            "time_based_patterns": self._detect_time_based_patterns,
            "correlation_patterns": self._detect_correlation_patterns,
            "session_patterns": self._detect_session_patterns,
            "page_navigation_patterns": self._detect_page_navigation_patterns
        }
        
        # Dictionnaire pour stocker les patterns détectés
        self.detected_patterns = {}
        
        logger.info("PatternDetector initialized")
    
    def detect_patterns(self, user_id: Optional[str] = None, start_date: Optional[datetime] = None, 
                       end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Détecte les patterns comportementaux pour un utilisateur ou tous les utilisateurs.
        
        Args:
            user_id: Identifiant de l'utilisateur (optionnel, sinon pour tous les utilisateurs)
            start_date: Date de début pour l'analyse (par défaut: 30 jours en arrière)
            end_date: Date de fin pour l'analyse (par défaut: maintenant)
            
        Returns:
            Dict contenant les patterns détectés
        """
        # Définir les dates par défaut si non spécifiées
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=30)
        
        logger.info(f"Detecting patterns for user_id={user_id} from {start_date} to {end_date}")
        
        # Récupérer les données de tracking
        if user_id:
            raw_data = self._get_user_tracking_data(user_id, start_date, end_date)
            
            if not raw_data or len(raw_data) == 0:
                logger.warning(f"No tracking data found for user {user_id}")
                return {}
                
            # Détecter les patterns pour cet utilisateur
            patterns = self._detect_user_patterns(user_id, raw_data)
            
            # Sauvegarder les patterns détectés
            self._save_user_patterns(user_id, patterns)
            
            return patterns
        else:
            # Récupérer les données de tracking pour tous les utilisateurs
            raw_data = self._get_all_tracking_data(start_date, end_date)
            
            if not raw_data or len(raw_data) == 0:
                logger.warning("No tracking data found for analysis")
                return {}
                
            # Détecter les patterns globaux
            patterns = self._detect_global_patterns(raw_data)
            
            # Sauvegarder les patterns détectés
            self._save_global_patterns(patterns)
            
            return patterns
    
    def get_user_patterns(self, user_id: str) -> Dict[str, Any]:
        """
        Récupère les patterns détectés pour un utilisateur spécifique.
        
        Args:
            user_id: Identifiant de l'utilisateur
            
        Returns:
            Dict contenant les patterns détectés pour l'utilisateur
        """
        # Vérifier si les patterns sont en mémoire
        if user_id in self.detected_patterns:
            logger.info(f"Returning cached patterns for user {user_id}")
            return self.detected_patterns[user_id]
        
        # Sinon, essayer de charger depuis le stockage
        pattern_path = os.path.join(self.storage_path, f"user_{user_id}_patterns.json")
        if os.path.exists(pattern_path):
            try:
                with open(pattern_path, 'r') as file:
                    patterns = json.load(file)
                    
                # Mettre en cache pour accès ultérieur
                self.detected_patterns[user_id] = patterns
                logger.info(f"Loaded patterns from storage for user {user_id}")
                return patterns
            except Exception as e:
                logger.error(f"Failed to load patterns from file: {str(e)}")
        
        logger.warning(f"No patterns found for user {user_id}")
        return {}
    
    def get_global_patterns(self) -> Dict[str, Any]:
        """
        Récupère les patterns globaux détectés.
        
        Returns:
            Dict contenant les patterns globaux
        """
        # Vérifier si les patterns sont en mémoire
        if "global" in self.detected_patterns:
            logger.info("Returning cached global patterns")
            return self.detected_patterns["global"]
        
        # Sinon, essayer de charger depuis le stockage
        pattern_path = os.path.join(self.storage_path, "global_patterns.json")
        if os.path.exists(pattern_path):
            try:
                with open(pattern_path, 'r') as file:
                    patterns = json.load(file)
                    
                # Mettre en cache pour accès ultérieur
                self.detected_patterns["global"] = patterns
                logger.info("Loaded global patterns from storage")
                return patterns
            except Exception as e:
                logger.error(f"Failed to load global patterns from file: {str(e)}")
        
        logger.warning("No global patterns found")
        return {}
    
    def get_similar_patterns(self, user_id: str) -> Dict[str, Any]:
        """
        Compare les patterns d'un utilisateur avec les patterns globaux.
        
        Args:
            user_id: Identifiant de l'utilisateur
            
        Returns:
            Dict contenant les similarités et différences entre patterns
        """
        # Récupérer les patterns de l'utilisateur
        user_patterns = self.get_user_patterns(user_id)
        if not user_patterns:
            logger.warning(f"No patterns found for user {user_id}")
            return {}
        
        # Récupérer les patterns globaux
        global_patterns = self.get_global_patterns()
        if not global_patterns:
            logger.warning("No global patterns found")
            return {}
        
        # Comparer les patterns
        comparison = {
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "similarities": {},
            "differences": {},
            "recommendations": []
        }
        
        # Comparer les patterns de séquence
        if "sequence_patterns" in user_patterns and "sequence_patterns" in global_patterns:
            user_sequences = set(tuple(seq["sequence"]) for seq in user_patterns["sequence_patterns"])
            global_sequences = set(tuple(seq["sequence"]) for seq in global_patterns["sequence_patterns"])
            
            common_sequences = user_sequences.intersection(global_sequences)
            unique_user_sequences = user_sequences - global_sequences
            unique_global_sequences = global_sequences - user_sequences
            
            comparison["similarities"]["common_sequences"] = [list(seq) for seq in common_sequences]
            comparison["differences"]["unique_user_sequences"] = [list(seq) for seq in unique_user_sequences]
            comparison["differences"]["unique_global_sequences"] = [list(seq) for seq in unique_global_sequences]
        
        # Comparer les patterns temporels
        if "time_based_patterns" in user_patterns and "time_based_patterns" in global_patterns:
            user_active_days = set(user_patterns["time_based_patterns"].get("active_days", []))
            global_active_days = set(global_patterns["time_based_patterns"].get("active_days", []))
            
            common_days = user_active_days.intersection(global_active_days)
            unique_user_days = user_active_days - global_active_days
            
            comparison["similarities"]["common_active_days"] = list(common_days)
            comparison["differences"]["unique_user_days"] = list(unique_user_days)
        
        # Générer des recommandations
        self._generate_recommendations(comparison, user_patterns, global_patterns)
        
        logger.info(f"Generated pattern comparison for user {user_id}")
        return comparison
    
    def _get_user_tracking_data(self, user_id: str, start_date: datetime, 
                              end_date: datetime) -> List[Dict[str, Any]]:
        """
        Récupère les données de tracking pour un utilisateur spécifique.
        
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
    
    def _get_all_tracking_data(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Récupère les données de tracking pour tous les utilisateurs.
        
        Args:
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
                WHERE timestamp BETWEEN '{start_date.isoformat()}' AND '{end_date.isoformat()}'
                ORDER BY timestamp ASC
                """
                return self.db_connector.execute_query(query)
            except Exception as e:
                logger.error(f"Error retrieving tracking data: {str(e)}")
                return []
        
        # Sinon, générer des données simulées pour plusieurs utilisateurs
        all_data = []
        for i in range(10):  # Simuler 10 utilisateurs
            user_id = f"user_{i}"
            user_data = self._generate_mock_tracking_data(user_id, start_date, end_date)
            all_data.extend(user_data)
        
        return all_data
    
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
            
            # Générer une session ou deux pour la journée
            session_count = np.random.randint(1, 3)
            for session_id in range(session_count):
                session_start = base_date + timedelta(seconds=np.random.randint(0, 86400 - 3600))
                session_events = np.random.randint(3, events_count // session_count)
                
                # Pages visitées dans cette session
                pages = [f"/page/{p}" for p in np.random.choice(range(1, 20), size=10, replace=True)]
                page_index = 0
                
                # Types d'événements plus probables pour simuler des patterns
                if np.random.random() < 0.7:
                    # Session type A: plus de page_view et clicks
                    session_probs = [0.5, 0.3, 0.1, 0.05, 0.03, 0.02]
                else:
                    # Session type B: plus de search et filter
                    session_probs = [0.3, 0.2, 0.25, 0.15, 0.05, 0.05]
                
                for i in range(session_events):
                    # Événements espacés dans le temps
                    event_time = session_start + timedelta(seconds=np.random.randint(0, 3600))
                    
                    # Type d'événement selon les probabilités de cette session
                    event_type = np.random.choice(event_types, p=session_probs)
                    
                    # Simuler une navigation entre pages
                    if event_type == "page_view":
                        page_index = min(page_index + 1, len(pages) - 1)
                    
                    event = {
                        "user_id": user_id,
                        "timestamp": event_time.isoformat(),
                        "event_type": event_type,
                        "session_id": f"session_{day_offset}_{session_id}",
                        "page": pages[page_index],
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
    
    def _detect_user_patterns(self, user_id: str, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Détecte les patterns comportementaux pour un utilisateur spécifique.
        
        Args:
            user_id: Identifiant de l'utilisateur
            data: Données de tracking de l'utilisateur
            
        Returns:
            Dict contenant les patterns détectés
        """
        patterns = {
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "data_count": len(data)
        }
        
        # Détecter tous les types de patterns
        for pattern_type, detector_func in self.pattern_types.items():
            try:
                patterns[pattern_type] = detector_func(data, user_specific=True)
            except Exception as e:
                logger.error(f"Error detecting {pattern_type}: {str(e)}")
                patterns[pattern_type] = {}
        
        logger.info(f"Detected patterns for user {user_id}")
        return patterns
    
    def _detect_global_patterns(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Détecte les patterns comportementaux globaux.
        
        Args:
            data: Données de tracking de tous les utilisateurs
            
        Returns:
            Dict contenant les patterns globaux détectés
        """
        patterns = {
            "timestamp": datetime.now().isoformat(),
            "data_count": len(data),
            "user_count": len(set(event["user_id"] for event in data))
        }
        
        # Détecter tous les types de patterns
        for pattern_type, detector_func in self.pattern_types.items():
            try:
                patterns[pattern_type] = detector_func(data, user_specific=False)
            except Exception as e:
                logger.error(f"Error detecting {pattern_type}: {str(e)}")
                patterns[pattern_type] = {}
        
        logger.info("Detected global patterns")
        return patterns
    
    def _detect_sequence_patterns(self, data: List[Dict[str, Any]], user_specific: bool) -> Dict[str, Any]:
        """
        Détecte les séquences d'événements qui se répètent dans les données.
        
        Args:
            data: Données de tracking
            user_specific: True si l'analyse est spécifique à un utilisateur
            
        Returns:
            Dict contenant les patterns de séquence détectés
        """
        # Extraire les séquences d'événements
        sequences = []
        
        if user_specific:
            # Pour un utilisateur spécifique, on peut simplement regarder les séquences d'événements
            events = [event["event_type"] for event in data]
            
            # Rechercher les séquences de longueur 3
            seq_length = 3
            for i in range(len(events) - seq_length + 1):
                sequences.append(tuple(events[i:i + seq_length]))
        else:
            # Pour les patterns globaux, on regroupe par utilisateur et session
            sessions = defaultdict(list)
            
            for event in data:
                user_id = event["user_id"]
                session_id = event.get("session_id", "unknown")
                key = f"{user_id}_{session_id}"
                sessions[key].append(event["event_type"])
            
            # Extraire les séquences de chaque session
            seq_length = 3
            for session_events in sessions.values():
                if len(session_events) >= seq_length:
                    for i in range(len(session_events) - seq_length + 1):
                        sequences.append(tuple(session_events[i:i + seq_length]))
        
        # Compter les séquences
        sequence_counts = Counter(sequences)
        
        # Filtrer les séquences qui apparaissent au moins 2 fois
        common_sequences = [
            {"sequence": list(seq), "count": count}
            for seq, count in sequence_counts.most_common(10)
            if count >= 2
        ]
        
        return common_sequences
    
    def _detect_time_based_patterns(self, data: List[Dict[str, Any]], user_specific: bool) -> Dict[str, Any]:
        """
        Détecte les patterns temporels dans les données.
        
        Args:
            data: Données de tracking
            user_specific: True si l'analyse est spécifique à un utilisateur
            
        Returns:
            Dict contenant les patterns temporels détectés
        """
        # Initialiser les compteurs
        hour_counts = [0] * 24
        day_counts = [0] * 7
        
        # Compter les événements par heure et jour de la semaine
        for event in data:
            try:
                timestamp = datetime.fromisoformat(event["timestamp"])
                hour_counts[timestamp.hour] += 1
                day_counts[timestamp.weekday()] += 1
            except (ValueError, KeyError):
                continue
        
        # Normaliser les compteurs
        total_events = len(data)
        hour_distribution = [count / total_events if total_events > 0 else 0 for count in hour_counts]
        day_distribution = [count / total_events if total_events > 0 else 0 for count in day_counts]
        
        # Déterminer les heures actives (pics d'activité)
        hour_threshold = np.mean(hour_distribution) * 1.5
        active_hours = [hour for hour, count in enumerate(hour_distribution) if count >= hour_threshold]
        
        # Déterminer les jours actifs
        day_threshold = np.mean(day_distribution) * 1.5
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        active_days = [day_names[day] for day, count in enumerate(day_distribution) if count >= day_threshold]
        
        # Calculer les intervalles entre sessions
        session_intervals = []
        
        if user_specific:
            # Extraire les timestamps des débuts de session
            sessions = defaultdict(list)
            
            for event in data:
                session_id = event.get("session_id", "unknown")
                try:
                    timestamp = datetime.fromisoformat(event["timestamp"])
                    sessions[session_id].append(timestamp)
                except (ValueError, KeyError):
                    continue
            
            # Extraire la première timestamp de chaque session
            session_starts = [min(timestamps) for timestamps in sessions.values()]
            session_starts.sort()
            
            # Calculer les intervalles entre sessions
            for i in range(1, len(session_starts)):
                interval = (session_starts[i] - session_starts[i-1]).total_seconds() / 3600  # en heures
                if interval < 168:  # ignorer les intervalles de plus d'une semaine
                    session_intervals.append(interval)
        
        # Déterminer les schémas de retour (périodicité)
        return_patterns = {}
        if session_intervals:
            # Calculer les statistiques des intervalles
            avg_interval = np.mean(session_intervals)
            median_interval = np.median(session_intervals)
            
            # Déterminer la périodicité dominante
            if 20 <= avg_interval <= 28:
                return_patterns["periodicity"] = "daily"
            elif 140 <= avg_interval <= 196:
                return_patterns["periodicity"] = "weekly"
            else:
                return_patterns["periodicity"] = "irregular"
                
            return_patterns["avg_interval_hours"] = avg_interval
            return_patterns["median_interval_hours"] = median_interval
        
        return {
            "hour_distribution": dict(enumerate(hour_distribution)),
            "day_distribution": dict(zip(day_names, day_distribution)),
            "active_hours": active_hours,
            "active_days": active_days,
            "return_patterns": return_patterns
        }
    
    def _detect_correlation_patterns(self, data: List[Dict[str, Any]], user_specific: bool) -> Dict[str, Any]:
        """
        Détecte les corrélations entre différents types d'événements.
        
        Args:
            data: Données de tracking
            user_specific: True si l'analyse est spécifique à un utilisateur
            
        Returns:
            Dict contenant les patterns de corrélation détectés
        """
        # Compteur pour les paires d'événements
        event_pairs = Counter()
        
        # Analyser les paires d'événements dans les sessions
        sessions = defaultdict(list)
        
        for event in data:
            user_id = event["user_id"]
            session_id = event.get("session_id", "unknown")
            key = f"{user_id}_{session_id}"
            sessions[key].append(event["event_type"])
        
        # Compter les co-occurrences d'événements dans les sessions
        for session_events in sessions.values():
            # Utiliser seulement les types d'événements uniques dans la session
            unique_events = set(session_events)
            
            # Générer toutes les paires possibles
            for pair in combinations(unique_events, 2):
                event_pairs[pair] += 1
        
        # Filtrer les paires qui apparaissent fréquemment
        threshold = max(3, len(sessions) * 0.1)  # Au moins 3 occurrences ou 10% des sessions
        
        # Extraire les co-occurrences significatives
        correlations = [
            {"events": list(pair), "count": count}
            for pair, count in event_pairs.most_common(10)
            if count >= threshold
        ]
        
        # Calculer les associations (si un événement X se produit, quelle est la probabilité d'un événement Y)
        associations = []
        event_counts = Counter(event["event_type"] for event in data)
        
        for pair, count in event_pairs.most_common(20):
            if count >= threshold:
                event_a, event_b = pair
                count_a = event_counts[event_a]
                count_b = event_counts[event_b]
                
                if count_a > 0 and count_b > 0:
                    prob_a_given_b = count / count_b
                    prob_b_given_a = count / count_a
                    
                    associations.append({
                        "events": list(pair),
                        "count": count,
                        "probability_a_given_b": prob_a_given_b,
                        "probability_b_given_a": prob_b_given_a
                    })
        
        return {
            "correlations": correlations,
            "associations": associations[:5]  # Limiter aux 5 meilleures associations
        }
    
    def _detect_session_patterns(self, data: List[Dict[str, Any]], user_specific: bool) -> Dict[str, Any]:
        """
        Détecte les patterns au niveau des sessions.
        
        Args:
            data: Données de tracking
            user_specific: True si l'analyse est spécifique à un utilisateur
            
        Returns:
            Dict contenant les patterns de session détectés
        """
        # Regrouper les événements par session
        sessions = defaultdict(list)
        
        for event in data:
            user_id = event["user_id"]
            session_id = event.get("session_id", "unknown")
            key = f"{user_id}_{session_id}"
            
            try:
                timestamp = datetime.fromisoformat(event["timestamp"])
                sessions[key].append({
                    "event_type": event["event_type"],
                    "timestamp": timestamp,
                    "page": event.get("page", ""),
                    "properties": event.get("properties", {})
                })
            except (ValueError, KeyError):
                continue
        
        # Calculer les statistiques des sessions
        session_stats = {
            "count": len(sessions),
            "avg_length": 0,
            "avg_duration_seconds": 0,
            "common_first_events": Counter(),
            "common_last_events": Counter(),
            "funnel_patterns": [],
            "session_types": {}
        }
        
        session_durations = []
        session_lengths = []
        
        for session_id, events in sessions.items():
            # Trier les événements par timestamp
            events.sort(key=lambda x: x["timestamp"])
            
            # Calculer la durée de la session
            if len(events) >= 2:
                duration = (events[-1]["timestamp"] - events[0]["timestamp"]).total_seconds()
                session_durations.append(duration)
            
            # Longueur de la session (nombre d'événements)
            session_lengths.append(len(events))
            
            # Premier et dernier événement
            if events:
                session_stats["common_first_events"][events[0]["event_type"]] += 1
                session_stats["common_last_events"][events[-1]["event_type"]] += 1
            
            # Détecter les patterns d'entonnoir (funnel)
            self._detect_funnel_patterns(events, session_stats["funnel_patterns"])
            
            # Catégoriser la session
            session_type = self._categorize_session(events)
            if session_type:
                if session_type not in session_stats["session_types"]:
                    session_stats["session_types"][session_type] = 0
                session_stats["session_types"][session_type] += 1
        
        # Calculer les moyennes
        if session_lengths:
            session_stats["avg_length"] = np.mean(session_lengths)
        if session_durations:
            session_stats["avg_duration_seconds"] = np.mean(session_durations)
        
        # Extraire les événements les plus communs au début et à la fin
        session_stats["common_first_events"] = [
            {"event_type": event, "count": count}
            for event, count in session_stats["common_first_events"].most_common(3)
        ]
        
        session_stats["common_last_events"] = [
            {"event_type": event, "count": count}
            for event, count in session_stats["common_last_events"].most_common(3)
        ]
        
        # Conserver uniquement les patterns d'entonnoir les plus fréquents
        session_stats["funnel_patterns"] = sorted(
            session_stats["funnel_patterns"], 
            key=lambda x: x["count"], 
            reverse=True
        )[:5]
        
        # Convertir les compteurs de types de session en pourcentages
        total_sessions = len(sessions)
        if total_sessions > 0:
            for session_type in session_stats["session_types"]:
                session_stats["session_types"][session_type] = round(
                    session_stats["session_types"][session_type] / total_sessions * 100, 1
                )
        
        return session_stats
    
    def _detect_funnel_patterns(self, events: List[Dict[str, Any]], funnel_patterns: List[Dict[str, Any]]) -> None:
        """
        Détecte les patterns d'entonnoir (funnel) dans une session.
        
        Args:
            events: Liste des événements dans une session
            funnel_patterns: Liste à mettre à jour avec les patterns détectés
        """
        # Patterns d'entonnoir prédéfinis à rechercher
        funnels = [
            {
                "name": "Search to Apply",
                "steps": ["search", "click", "apply"],
                "strict_order": False
            },
            {
                "name": "Search to Download",
                "steps": ["search", "click", "download"],
                "strict_order": False
            },
            {
                "name": "Filter to Apply",
                "steps": ["filter", "click", "apply"],
                "strict_order": False
            },
            {
                "name": "Complete Application",
                "steps": ["page_view", "click", "download", "apply"],
                "strict_order": True
            }
        ]
        
        event_types = [event["event_type"] for event in events]
        
        for funnel in funnels:
            if funnel["strict_order"]:
                # Rechercher la séquence exacte
                for i in range(len(event_types) - len(funnel["steps"]) + 1):
                    if event_types[i:i+len(funnel["steps"])] == funnel["steps"]:
                        # Trouver le pattern existant ou en créer un nouveau
                        found = False
                        for pattern in funnel_patterns:
                            if pattern["name"] == funnel["name"]:
                                pattern["count"] += 1
                                found = True
                                break
                        if not found:
                            funnel_patterns.append({
                                "name": funnel["name"],
                                "steps": funnel["steps"],
                                "count": 1
                            })
                        break
            else:
                # Vérifier si tous les étapes sont présentes, dans n'importe quel ordre
                if all(step in event_types for step in funnel["steps"]):
                    # Trouver le pattern existant ou en créer un nouveau
                    found = False
                    for pattern in funnel_patterns:
                        if pattern["name"] == funnel["name"]:
                            pattern["count"] += 1
                            found = True
                            break
                    if not found:
                        funnel_patterns.append({
                            "name": funnel["name"],
                            "steps": funnel["steps"],
                            "count": 1
                        })
    
    def _categorize_session(self, events: List[Dict[str, Any]]) -> Optional[str]:
        """
        Catégorise une session selon le comportement dominant.
        
        Args:
            events: Liste des événements dans une session
            
        Returns:
            Type de session ou None
        """
        if not events:
            return None
        
        # Compter les types d'événements
        event_counts = Counter(event["event_type"] for event in events)
        total_events = len(events)
        
        # Calculer les proportions
        proportions = {event_type: count / total_events for event_type, count in event_counts.items()}
        
        # Règles de catégorisation
        if "apply" in proportions:
            return "Application"
        elif proportions.get("search", 0) > 0.3:
            return "Search Intensive"
        elif proportions.get("filter", 0) > 0.2:
            return "Filtering"
        elif proportions.get("download", 0) > 0.1:
            return "Document Review"
        elif proportions.get("click", 0) > 0.5:
            return "Browsing"
        elif total_events < 3:
            return "Brief Visit"
        else:
            return "General"
    
    def _detect_page_navigation_patterns(self, data: List[Dict[str, Any]], user_specific: bool) -> Dict[str, Any]:
        """
        Détecte les patterns de navigation entre pages.
        
        Args:
            data: Données de tracking
            user_specific: True si l'analyse est spécifique à un utilisateur
            
        Returns:
            Dict contenant les patterns de navigation détectés
        """
        # Créer un graphe dirigé pour représenter les transitions entre pages
        graph = nx.DiGraph()
        
        # Regrouper par session
        sessions = defaultdict(list)
        for event in data:
            if event.get("event_type") == "page_view" and event.get("page"):
                user_id = event["user_id"]
                session_id = event.get("session_id", "unknown")
                key = f"{user_id}_{session_id}"
                
                try:
                    timestamp = datetime.fromisoformat(event["timestamp"])
                    sessions[key].append({
                        "page": event["page"],
                        "timestamp": timestamp
                    })
                except (ValueError, KeyError):
                    continue
        
        # Analyser les transitions entre pages
        transitions = Counter()
        for session_id, events in sessions.items():
            # Trier les événements par timestamp
            events.sort(key=lambda x: x["timestamp"])
            
            # Extraire les pages visitées
            pages = [event["page"] for event in events]
            
            # Ajouter les nœuds au graphe
            for page in pages:
                if page not in graph:
                    graph.add_node(page)
            
            # Ajouter les transitions
            for i in range(len(pages) - 1):
                source = pages[i]
                target = pages[i + 1]
                
                # Mettre à jour le compteur
                transitions[(source, target)] += 1
                
                # Mettre à jour le graphe
                if graph.has_edge(source, target):
                    graph[source][target]["weight"] += 1
                else:
                    graph.add_edge(source, target, weight=1)
        
        # Calculer les pages d'entrée et de sortie
        entry_pages = Counter()
        exit_pages = Counter()
        
        for session_id, events in sessions.items():
            if events:
                entry_pages[events[0]["page"]] += 1
                exit_pages[events[-1]["page"]] += 1
        
        # Extraire les chemins les plus fréquents
        common_paths = []
        for path, count in transitions.most_common(10):
            source, target = path
            common_paths.append({
                "source": source,
                "target": target,
                "count": count
            })
        
        # Calculer les mesures de centralité
        if graph.nodes():
            try:
                # Centralité de degré (popularité des pages)
                degree_centrality = nx.degree_centrality(graph)
                
                # Centralité intermédiaire (pages de passage)
                betweenness_centrality = nx.betweenness_centrality(graph, weight="weight")
                
                # Centralité de proximité (pages accessibles)
                closeness_centrality = nx.closeness_centrality(graph)
                
                # Convertir en formats plus simples
                centrality = {
                    "degree": dict(sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:5]),
                    "betweenness": dict(sorted(betweenness_centrality.items(), key=lambda x: x[1], reverse=True)[:5]),
                    "closeness": dict(sorted(closeness_centrality.items(), key=lambda x: x[1], reverse=True)[:5])
                }
            except Exception as e:
                logger.error(f"Error calculating centrality: {str(e)}")
                centrality = {}
        else:
            centrality = {}
        
        return {
            "common_paths": common_paths,
            "entry_pages": [{"page": page, "count": count} for page, count in entry_pages.most_common(5)],
            "exit_pages": [{"page": page, "count": count} for page, count in exit_pages.most_common(5)],
            "centrality": centrality
        }
    
    def _generate_recommendations(self, comparison: Dict[str, Any], user_patterns: Dict[str, Any], 
                                global_patterns: Dict[str, Any]) -> None:
        """
        Génère des recommandations basées sur la comparaison des patterns.
        
        Args:
            comparison: Comparaison des patterns
            user_patterns: Patterns de l'utilisateur
            global_patterns: Patterns globaux
        """
        recommendations = []
        
        # Recommandations basées sur les sessions
        if "session_patterns" in user_patterns and "session_patterns" in global_patterns:
            user_session = user_patterns["session_patterns"]
            global_session = global_patterns["session_patterns"]
            
            # Recommandation si l'utilisateur a des sessions courtes
            if user_session.get("avg_duration_seconds", 0) < global_session.get("avg_duration_seconds", 0) * 0.7:
                recommendations.append({
                    "type": "engagement",
                    "message": "L'utilisateur a des sessions plus courtes que la moyenne. Proposer du contenu plus ciblé pour augmenter l'engagement."
                })
            
            # Recommandation basée sur les types de session
            user_types = set(user_session.get("session_types", {}).keys())
            global_types = set(global_session.get("session_types", {}).keys())
            
            missing_types = global_types - user_types
            for session_type in missing_types:
                if session_type == "Application":
                    recommendations.append({
                        "type": "conversion",
                        "message": "L'utilisateur n'a pas de sessions d'application. Proposer des offres plus adaptées pour encourager les candidatures."
                    })
                elif session_type == "Document Review":
                    recommendations.append({
                        "type": "content",
                        "message": "L'utilisateur consulte peu de documents. Mettre en avant des documents pertinents pour susciter l'intérêt."
                    })
        
        # Recommandations basées sur les patterns temporels
        if "time_based_patterns" in user_patterns and "time_based_patterns" in global_patterns:
            user_time = user_patterns["time_based_patterns"]
            global_time = global_patterns["time_based_patterns"]
            
            # Recommandation basée sur les jours actifs
            user_days = set(user_time.get("active_days", []))
            global_days = set(global_time.get("active_days", []))
            
            if "Monday" in global_days and "Monday" not in user_days:
                recommendations.append({
                    "type": "timing",
                    "message": "L'utilisateur n'est pas actif le lundi, contrairement à la majorité. Envoyer des rappels ou newsletters le dimanche soir."
                })
        
        # Ajouter les recommandations à la comparaison
        comparison["recommendations"] = recommendations
    
    def _save_user_patterns(self, user_id: str, patterns: Dict[str, Any]) -> None:
        """
        Sauvegarde les patterns détectés pour un utilisateur.
        
        Args:
            user_id: Identifiant de l'utilisateur
            patterns: Patterns détectés
        """
        # Mettre en cache
        self.detected_patterns[user_id] = patterns
        
        # Sauvegarder dans un fichier
        pattern_path = os.path.join(self.storage_path, f"user_{user_id}_patterns.json")
        try:
            with open(pattern_path, 'w') as file:
                json.dump(patterns, file, indent=2)
            logger.info(f"Saved patterns for user {user_id} to {pattern_path}")
        except Exception as e:
            logger.error(f"Failed to save patterns to file: {str(e)}")
    
    def _save_global_patterns(self, patterns: Dict[str, Any]) -> None:
        """
        Sauvegarde les patterns globaux détectés.
        
        Args:
            patterns: Patterns globaux détectés
        """
        # Mettre en cache
        self.detected_patterns["global"] = patterns
        
        # Sauvegarder dans un fichier
        pattern_path = os.path.join(self.storage_path, "global_patterns.json")
        try:
            with open(pattern_path, 'w') as file:
                json.dump(patterns, file, indent=2)
            logger.info(f"Saved global patterns to {pattern_path}")
        except Exception as e:
            logger.error(f"Failed to save global patterns to file: {str(e)}")
