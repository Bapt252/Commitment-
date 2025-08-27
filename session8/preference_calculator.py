"""
Module de calcul des scores de préférence dynamiques.

Ce module est responsable du calcul des scores de préférence des utilisateurs
basés sur leur comportement et leurs interactions avec le système.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Any, Optional, Tuple
import json
import os

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class PreferenceCalculator:
    """
    Calculateur de scores de préférence dynamiques basés sur le comportement utilisateur.
    """
    
    def __init__(self, profile_manager=None, pattern_detector=None, db_connector=None, 
                 storage_path: str = "./preferences", config=None):
        """
        Initialise le calculateur de préférences.
        
        Args:
            profile_manager: Gestionnaire de profils utilisateurs
            pattern_detector: Détecteur de patterns comportementaux
            db_connector: Connecteur vers la base de données de tracking
            storage_path: Chemin vers le dossier de stockage des préférences
            config: Configuration supplémentaire
        """
        self.profile_manager = profile_manager
        self.pattern_detector = pattern_detector
        self.db_connector = db_connector
        self.storage_path = storage_path
        
        # Configuration par défaut
        self.config = {
            "preference_weights": {
                "content_preferences": 0.4,
                "interaction_preferences": 0.3,
                "time_preferences": 0.2,
                "feature_preferences": 0.1
            },
            "update_threshold_hours": 24,
            "scoring_methods": {
                "content_similarity": "weighted_overlap",
                "time_similarity": "gaussian",
                "feature_similarity": "cosine"
            }
        }
        
        # Mise à jour de la configuration si fournie
        if config:
            self.config.update(config)
        
        # Créer le dossier de stockage s'il n'existe pas
        os.makedirs(storage_path, exist_ok=True)
        
        # Définir les catégories de préférences à calculer
        self.preference_categories = {
            "content_preferences": self._calculate_content_preferences,
            "interaction_preferences": self._calculate_interaction_preferences,
            "time_preferences": self._calculate_time_preferences,
            "feature_preferences": self._calculate_feature_preferences
        }
        
        # Cache pour les préférences calculées
        self.preferences_cache = {}
        
        logger.info("PreferenceCalculator initialized")
    
    def calculate_preferences(self, user_id: str, start_date: Optional[datetime] = None, 
                             end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Calcule les scores de préférence pour un utilisateur spécifique.
        
        Args:
            user_id: Identifiant de l'utilisateur
            start_date: Date de début pour l'analyse (par défaut: 30 jours en arrière)
            end_date: Date de fin pour l'analyse (par défaut: maintenant)
            
        Returns:
            Dict contenant les scores de préférence calculés
        """
        logger.info(f"Calculating preferences for user {user_id}")
        
        # Définir les dates par défaut si non spécifiées
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=30)
        
        # Récupérer le profil et les patterns de l'utilisateur
        profile = None
        if self.profile_manager:
            profile = self.profile_manager.get_profile(user_id)
        
        patterns = None
        if self.pattern_detector:
            patterns = self.pattern_detector.get_user_patterns(user_id)
        
        # Récupérer les données de tracking si nécessaire
        raw_data = self._get_user_tracking_data(user_id, start_date, end_date)
        
        if not raw_data and not profile and not patterns:
            logger.warning(f"No data available for preference calculation for user {user_id}")
            return {}
        
        # Résultats globaux des préférences
        preferences = {
            "user_id": user_id,
            "calculation_date": datetime.now().isoformat(),
            "data_start_date": start_date.isoformat(),
            "data_end_date": end_date.isoformat()
        }
        
        # Calculer les différentes catégories de préférences
        for category, calculator in self.preference_categories.items():
            try:
                preferences[category] = calculator(user_id, raw_data, profile, patterns)
            except Exception as e:
                logger.error(f"Error calculating {category}: {str(e)}")
                preferences[category] = {}
        
        # Calculer un score global de préférence
        preferences["overall_score"] = self._calculate_overall_preference_score(preferences)
        
        # Sauvegarder les préférences calculées
        self._save_preferences(user_id, preferences)
        
        logger.info(f"Calculated preferences for user {user_id}")
        return preferences
    
    def get_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Récupère les préférences calculées pour un utilisateur.
        
        Args:
            user_id: Identifiant de l'utilisateur
            
        Returns:
            Dict contenant les préférences calculées
        """
        # Vérifier le cache d'abord
        if user_id in self.preferences_cache:
            logger.info(f"Returning cached preferences for user {user_id}")
            return self.preferences_cache[user_id]
        
        # Sinon, essayer de charger depuis le stockage
        preferences_path = os.path.join(self.storage_path, f"user_{user_id}_preferences.json")
        if os.path.exists(preferences_path):
            try:
                with open(preferences_path, 'r') as file:
                    preferences = json.load(file)
                    
                # Mettre en cache pour accès ultérieur
                self.preferences_cache[user_id] = preferences
                logger.info(f"Loaded preferences from storage for user {user_id}")
                return preferences
            except Exception as e:
                logger.error(f"Failed to load preferences from file: {str(e)}")
        
        logger.warning(f"No preferences found for user {user_id}, calculating new ones")
        return self.calculate_preferences(user_id)
    
    def get_recommendation_score(self, user_id: str, item_id: str, item_type: str) -> float:
        """
        Calcule un score de recommandation pour un élément spécifique basé sur les préférences.
        
        Args:
            user_id: Identifiant de l'utilisateur
            item_id: Identifiant de l'élément
            item_type: Type de l'élément (job, cv, etc.)
            
        Returns:
            Score de recommandation entre 0 et 1
        """
        # Récupérer les préférences de l'utilisateur
        preferences = self.get_preferences(user_id)
        if not preferences:
            logger.warning(f"No preferences available for recommendation score calculation for user {user_id}")
            return 0.5  # Score neutre par défaut
        
        # Récupérer les caractéristiques de l'élément (simulé ici)
        item_features = self._get_item_features(item_id, item_type)
        if not item_features:
            logger.warning(f"No features available for item {item_id} of type {item_type}")
            return 0.5  # Score neutre par défaut
        
        # Calculer le score de recommandation
        content_score = self._calculate_content_similarity(
            preferences.get("content_preferences", {}),
            item_features
        )
        
        # On pourrait ajouter d'autres aspects au score ici, comme la temporalité, etc.
        
        logger.info(f"Calculated recommendation score {content_score:.2f} for user {user_id} and item {item_id}")
        return content_score
    
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
        
        # Définir certaines préférences simulées pour l'utilisateur
        favorite_categories = np.random.choice(
            ["engineering", "marketing", "sales", "design", "finance"], 
            size=np.random.randint(1, 3),
            replace=False
        )
        favorite_locations = np.random.choice(
            ["paris", "lyon", "marseille", "bordeaux", "toulouse"], 
            size=np.random.randint(1, 3),
            replace=False
        )
        favorite_times = np.random.choice(
            ["morning", "afternoon", "evening", "night"], 
            size=np.random.randint(1, 3),
            replace=False
        )
        
        for day_offset in active_days:
            # Nombre d'événements par jour actif
            events_count = np.random.randint(5, 50)
            base_date = start_date + timedelta(days=day_offset)
            
            # Heure de la journée en fonction des préférences temporelles
            if "morning" in favorite_times:
                hour_range = (8, 12)
            elif "afternoon" in favorite_times:
                hour_range = (12, 18)
            elif "evening" in favorite_times:
                hour_range = (18, 22)
            elif "night" in favorite_times:
                hour_range = (22, 8)
            else:
                hour_range = (8, 22)
            
            # Générer des événements pour cette journée
            for _ in range(events_count):
                hour = np.random.randint(hour_range[0], hour_range[1])
                event_time = base_date.replace(hour=hour, minute=np.random.randint(0, 60))
                
                # Type d'événement avec une probabilité plus élevée pour les catégories préférées
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
                    element_types = ["button", "link", "card"]
                    event["properties"]["element_type"] = np.random.choice(element_types)
                    
                elif event_type == "search":
                    # Favoriser les catégories préférées dans les recherches
                    if np.random.random() < 0.7 and favorite_categories.size > 0:
                        category = np.random.choice(favorite_categories)
                        event["properties"]["query"] = f"{category} jobs"
                    else:
                        event["properties"]["query"] = f"query_{np.random.randint(1, 10)}"
                    
                    event["properties"]["results_count"] = np.random.randint(0, 50)
                    
                elif event_type == "filter":
                    filter_types = ["category", "location", "salary", "experience"]
                    filter_type = np.random.choice(filter_types)
                    event["properties"]["filter_type"] = filter_type
                    
                    if filter_type == "category" and np.random.random() < 0.8 and favorite_categories.size > 0:
                        # Favoriser les catégories préférées dans les filtres
                        event["properties"]["filter_value"] = np.random.choice(favorite_categories)
                    elif filter_type == "location" and np.random.random() < 0.8 and favorite_locations.size > 0:
                        # Favoriser les localisations préférées
                        event["properties"]["filter_value"] = np.random.choice(favorite_locations)
                    else:
                        event["properties"]["filter_value"] = f"value_{np.random.randint(1, 10)}"
                    
                elif event_type == "download":
                    doc_types = ["cv", "job", "report"]
                    event["properties"]["document_id"] = f"doc_{np.random.randint(1, 100)}"
                    event["properties"]["document_type"] = np.random.choice(doc_types)
                    
                    # Ajouter des métadonnées pour les documents
                    if event["properties"]["document_type"] == "job":
                        # Favoriser les catégories préférées
                        if np.random.random() < 0.7 and favorite_categories.size > 0:
                            event["properties"]["job_category"] = np.random.choice(favorite_categories)
                        else:
                            event["properties"]["job_category"] = np.random.choice(
                                ["engineering", "marketing", "sales", "design", "finance"]
                            )
                        
                        # Favoriser les localisations préférées
                        if np.random.random() < 0.7 and favorite_locations.size > 0:
                            event["properties"]["job_location"] = np.random.choice(favorite_locations)
                        else:
                            event["properties"]["job_location"] = np.random.choice(
                                ["paris", "lyon", "marseille", "bordeaux", "toulouse"]
                            )
                    
                elif event_type == "apply":
                    application_methods = ["direct", "email", "form"]
                    event["properties"]["job_id"] = f"job_{np.random.randint(1, 100)}"
                    event["properties"]["application_method"] = np.random.choice(application_methods)
                    
                    # Ajouter des métadonnées pour les offres d'emploi
                    if np.random.random() < 0.7 and favorite_categories.size > 0:
                        event["properties"]["job_category"] = np.random.choice(favorite_categories)
                    else:
                        event["properties"]["job_category"] = np.random.choice(
                            ["engineering", "marketing", "sales", "design", "finance"]
                        )
                    
                    if np.random.random() < 0.7 and favorite_locations.size > 0:
                        event["properties"]["job_location"] = np.random.choice(favorite_locations)
                    else:
                        event["properties"]["job_location"] = np.random.choice(
                            ["paris", "lyon", "marseille", "bordeaux", "toulouse"]
                        )
                
                mock_data.append(event)
        
        # Trier par timestamp
        mock_data.sort(key=lambda x: x["timestamp"])
        logger.info(f"Generated {len(mock_data)} mock events for user {user_id}")
        
        return mock_data
    
    def _calculate_content_preferences(self, user_id: str, raw_data: List[Dict[str, Any]], 
                                     profile: Optional[Dict[str, Any]], 
                                     patterns: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calcule les préférences de contenu basées sur les interactions.
        
        Args:
            user_id: Identifiant de l'utilisateur
            raw_data: Données de tracking brutes
            profile: Profil de l'utilisateur (optionnel)
            patterns: Patterns comportementaux détectés (optionnel)
            
        Returns:
            Dict contenant les préférences de contenu calculées
        """
        # Initialiser les compteurs
        categories = {}
        locations = {}
        salary_ranges = {}
        job_types = {}
        skills = {}
        industries = {}
        
        # Analyser les données de tracking
        for event in raw_data:
            props = event.get("properties", {})
            event_type = event.get("event_type")
            
            # Pondérer les événements selon leur importance
            weight = 1.0
            if event_type == "apply":
                weight = 5.0  # Les candidatures sont plus importantes
            elif event_type == "download":
                weight = 2.0  # Les téléchargements sont importants
            elif event_type == "search" or event_type == "filter":
                weight = 1.5  # Les recherches et filtres sont modérément importants
            
            # Extraire les catégories
            if "job_category" in props:
                category = props["job_category"]
                if category not in categories:
                    categories[category] = 0
                categories[category] += weight
            
            # Extraire les localisations
            if "job_location" in props:
                location = props["job_location"]
                if location not in locations:
                    locations[location] = 0
                locations[location] += weight
            
            # Extraire les plages de salaire
            if "salary_range" in props:
                salary = props["salary_range"]
                if salary not in salary_ranges:
                    salary_ranges[salary] = 0
                salary_ranges[salary] += weight
            
            # Extraire les types d'emploi
            if "job_type" in props:
                job_type = props["job_type"]
                if job_type not in job_types:
                    job_types[job_type] = 0
                job_types[job_type] += weight
            
            # Extraire les compétences
            if "skills" in props and isinstance(props["skills"], list):
                for skill in props["skills"]:
                    if skill not in skills:
                        skills[skill] = 0
                    skills[skill] += weight
            
            # Extraire les industries
            if "industry" in props:
                industry = props["industry"]
                if industry not in industries:
                    industries[industry] = 0
                industries[industry] += weight
            
            # Analyser les termes de recherche
            if event_type == "search" and "query" in props:
                query = props["query"].lower()
                
                # Recherche simple de mots-clés dans la requête
                for category in ["engineering", "marketing", "sales", "design", "finance"]:
                    if category in query:
                        if category not in categories:
                            categories[category] = 0
                        categories[category] += weight
                
                for location in ["paris", "lyon", "marseille", "bordeaux", "toulouse"]:
                    if location in query:
                        if location not in locations:
                            locations[location] = 0
                        locations[location] += weight
            
            # Analyser les filtres
            if event_type == "filter":
                filter_type = props.get("filter_type")
                filter_value = props.get("filter_value")
                
                if filter_type and filter_value:
                    if filter_type == "category":
                        if filter_value not in categories:
                            categories[filter_value] = 0
                        categories[filter_value] += weight
                    elif filter_type == "location":
                        if filter_value not in locations:
                            locations[filter_value] = 0
                        locations[filter_value] += weight
                    elif filter_type == "salary":
                        if filter_value not in salary_ranges:
                            salary_ranges[filter_value] = 0
                        salary_ranges[filter_value] += weight
        
        # Normaliser les scores
        categories = self._normalize_scores(categories)
        locations = self._normalize_scores(locations)
        salary_ranges = self._normalize_scores(salary_ranges)
        job_types = self._normalize_scores(job_types)
        skills = self._normalize_scores(skills)
        industries = self._normalize_scores(industries)
        
        # Extraire les top préférences
        top_categories = self._extract_top_preferences(categories, 3)
        top_locations = self._extract_top_preferences(locations, 3)
        top_salary_ranges = self._extract_top_preferences(salary_ranges, 2)
        top_job_types = self._extract_top_preferences(job_types, 2)
        top_skills = self._extract_top_preferences(skills, 5)
        top_industries = self._extract_top_preferences(industries, 3)
        
        return {
            "categories": categories,
            "locations": locations,
            "salary_ranges": salary_ranges,
            "job_types": job_types,
            "skills": skills,
            "industries": industries,
            "top_preferences": {
                "categories": top_categories,
                "locations": top_locations,
                "salary_ranges": top_salary_ranges,
                "job_types": top_job_types,
                "skills": top_skills,
                "industries": top_industries
            }
        }
    
    def _calculate_interaction_preferences(self, user_id: str, raw_data: List[Dict[str, Any]], 
                                        profile: Optional[Dict[str, Any]], 
                                        patterns: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calcule les préférences d'interaction basées sur le comportement.
        
        Args:
            user_id: Identifiant de l'utilisateur
            raw_data: Données de tracking brutes
            profile: Profil de l'utilisateur (optionnel)
            patterns: Patterns comportementaux détectés (optionnel)
            
        Returns:
            Dict contenant les préférences d'interaction calculées
        """
        # Initialiser les compteurs
        element_types = {}
        page_preferences = {}
        action_sequences = {}
        
        # Analyser les données de tracking
        for event in raw_data:
            # Extraire les types d'éléments cliqués
            if event.get("event_type") == "click":
                props = event.get("properties", {})
                element_type = props.get("element_type")
                
                if element_type:
                    if element_type not in element_types:
                        element_types[element_type] = 0
                    element_types[element_type] += 1
            
            # Extraire les préférences de page
            page = event.get("page")
            if page:
                if page not in page_preferences:
                    page_preferences[page] = 0
                page_preferences[page] += 1
        
        # Extraire les séquences d'actions si des patterns sont disponibles
        if patterns and "sequence_patterns" in patterns:
            for sequence in patterns["sequence_patterns"]:
                seq_key = "->".join(sequence.get("sequence", []))
                if seq_key:
                    action_sequences[seq_key] = sequence.get("count", 0)
        
        # Normaliser les scores
        element_types = self._normalize_scores(element_types)
        page_preferences = self._normalize_scores(page_preferences)
        action_sequences = self._normalize_scores(action_sequences)
        
        # Déterminer le mode d'interaction préféré
        interaction_mode = "explorer"  # Par défaut
        if element_types:
            if element_types.get("button", 0) > element_types.get("link", 0) and element_types.get("button", 0) > element_types.get("card", 0):
                interaction_mode = "direct"
            elif element_types.get("card", 0) > element_types.get("link", 0) and element_types.get("card", 0) > element_types.get("button", 0):
                interaction_mode = "visual"
            elif element_types.get("link", 0) > element_types.get("button", 0) and element_types.get("link", 0) > element_types.get("card", 0):
                interaction_mode = "explorer"
        
        # Extraire les top préférences
        top_pages = self._extract_top_preferences(page_preferences, 5)
        top_sequences = self._extract_top_preferences(action_sequences, 3)
        
        return {
            "element_types": element_types,
            "page_preferences": page_preferences,
            "action_sequences": action_sequences,
            "interaction_mode": interaction_mode,
            "top_preferences": {
                "pages": top_pages,
                "sequences": top_sequences
            }
        }
    
    def _calculate_time_preferences(self, user_id: str, raw_data: List[Dict[str, Any]], 
                                 profile: Optional[Dict[str, Any]], 
                                 patterns: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calcule les préférences temporelles basées sur les moments d'activité.
        
        Args:
            user_id: Identifiant de l'utilisateur
            raw_data: Données de tracking brutes
            profile: Profil de l'utilisateur (optionnel)
            patterns: Patterns comportementaux détectés (optionnel)
            
        Returns:
            Dict contenant les préférences temporelles calculées
        """
        # Initialiser les compteurs
        hour_counts = {str(h): 0 for h in range(24)}
        day_counts = {
            "Monday": 0, "Tuesday": 0, "Wednesday": 0, 
            "Thursday": 0, "Friday": 0, "Saturday": 0, "Sunday": 0
        }
        
        # Analyser les données de tracking ou utiliser les patterns existants
        if patterns and "time_based_patterns" in patterns and patterns["time_based_patterns"]:
            time_patterns = patterns["time_based_patterns"]
            
            # Extraire la distribution par heure
            if "hour_distribution" in time_patterns:
                for hour, value in time_patterns["hour_distribution"].items():
                    hour_counts[hour] = value
            
            # Extraire la distribution par jour
            if "day_distribution" in time_patterns:
                for day, value in time_patterns["day_distribution"].items():
                    day_counts[day] = value
        else:
            # Analyser les données de tracking
            for event in raw_data:
                try:
                    timestamp = datetime.fromisoformat(event["timestamp"])
                    hour = str(timestamp.hour)
                    day = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][timestamp.weekday()]
                    
                    hour_counts[hour] += 1
                    day_counts[day] += 1
                except (ValueError, KeyError):
                    continue
        
        # Déterminer les périodes préférées
        morning_score = sum(hour_counts.get(str(h), 0) for h in range(5, 12))  # 5h-12h
        afternoon_score = sum(hour_counts.get(str(h), 0) for h in range(12, 18))  # 12h-18h
        evening_score = sum(hour_counts.get(str(h), 0) for h in range(18, 23))  # 18h-23h
        night_score = sum(hour_counts.get(str(h), 0) for h in [23, 0, 1, 2, 3, 4])  # 23h-5h
        
        # Déterminer la période préférée
        time_of_day = "afternoon"  # Par défaut
        max_score = afternoon_score
        
        if morning_score > max_score:
            time_of_day = "morning"
            max_score = morning_score
        if evening_score > max_score:
            time_of_day = "evening"
            max_score = evening_score
        if night_score > max_score:
            time_of_day = "night"
        
        # Déterminer les jours préférés (semaine vs weekend)
        weekday_score = sum(day_counts.get(day, 0) for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
        weekend_score = sum(day_counts.get(day, 0) for day in ["Saturday", "Sunday"])
        
        day_preference = "weekday" if weekday_score > weekend_score else "weekend"
        
        # Normaliser les scores
        total_hour = sum(hour_counts.values())
        normalized_hours = {hour: count / total_hour if total_hour > 0 else 0 for hour, count in hour_counts.items()}
        
        total_day = sum(day_counts.values())
        normalized_days = {day: count / total_day if total_day > 0 else 0 for day, count in day_counts.items()}
        
        return {
            "hour_distribution": normalized_hours,
            "day_distribution": normalized_days,
            "preferred_time": time_of_day,
            "preferred_days": day_preference,
            "time_scores": {
                "morning": morning_score / total_hour if total_hour > 0 else 0,
                "afternoon": afternoon_score / total_hour if total_hour > 0 else 0,
                "evening": evening_score / total_hour if total_hour > 0 else 0,
                "night": night_score / total_hour if total_hour > 0 else 0
            },
            "day_scores": {
                "weekday": weekday_score / total_day if total_day > 0 else 0,
                "weekend": weekend_score / total_day if total_day > 0 else 0
            }
        }
    
    def _calculate_feature_preferences(self, user_id: str, raw_data: List[Dict[str, Any]], 
                                    profile: Optional[Dict[str, Any]], 
                                    patterns: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calcule les préférences pour les fonctionnalités de la plateforme.
        
        Args:
            user_id: Identifiant de l'utilisateur
            raw_data: Données de tracking brutes
            profile: Profil de l'utilisateur (optionnel)
            patterns: Patterns comportementaux détectés (optionnel)
            
        Returns:
            Dict contenant les préférences de fonctionnalités calculées
        """
        # Initialiser les compteurs pour les fonctionnalités
        features = {
            "search": 0,
            "filter": 0,
            "download": 0,
            "apply": 0,
            "recommendations": 0,
            "notifications": 0,
            "messaging": 0,
            "profile": 0
        }
        
        # Analyser les données de tracking
        for event in raw_data:
            event_type = event.get("event_type")
            page = event.get("page", "")
            props = event.get("properties", {})
            
            # Compter les utilisations directes des fonctionnalités
            if event_type in features:
                features[event_type] += 1
            
            # Détecter l'utilisation indirecte via les pages visitées
            if "recommendations" in page.lower():
                features["recommendations"] += 1
            elif "notifications" in page.lower():
                features["notifications"] += 1
            elif "message" in page.lower() or "chat" in page.lower():
                features["messaging"] += 1
            elif "profile" in page.lower() or "account" in page.lower():
                features["profile"] += 1
            
            # Détecter l'utilisation via les clics
            if event_type == "click":
                element_id = props.get("element_id", "")
                if "recommendation" in element_id.lower():
                    features["recommendations"] += 1
                elif "notification" in element_id.lower():
                    features["notifications"] += 1
                elif "message" in element_id.lower() or "chat" in element_id.lower():
                    features["messaging"] += 1
                elif "profile" in element_id.lower() or "account" in element_id.lower():
                    features["profile"] += 1
        
        # Normaliser les scores
        features = self._normalize_scores(features)
        
        # Déterminer les fonctionnalités préférées
        top_features = self._extract_top_preferences(features, 3)
        
        # Calculer un score de sophistication (préférence pour les fonctionnalités avancées)
        basic_features = features.get("search", 0) + features.get("filter", 0)
        advanced_features = features.get("recommendations", 0) + features.get("messaging", 0)
        
        sophistication_score = 0.5  # Score neutre par défaut
        total_usage = basic_features + advanced_features
        if total_usage > 0:
            sophistication_score = advanced_features / total_usage
        
        return {
            "feature_usage": features,
            "top_features": top_features,
            "sophistication_score": sophistication_score
        }
    
    def _calculate_overall_preference_score(self, preferences: Dict[str, Any]) -> Dict[str, float]:
        """
        Calcule un score global de préférence.
        
        Args:
            preferences: Dictionnaire des préférences calculées
            
        Returns:
            Dict contenant les scores globaux
        """
        # Extraire les top préférences de contenu
        content_prefs = preferences.get("content_preferences", {}).get("top_preferences", {})
        
        # Calculer le score de contenu
        content_score = 0.0
        if content_prefs:
            category_weights = sum(weight for _, weight in content_prefs.get("categories", {}).items())
            location_weights = sum(weight for _, weight in content_prefs.get("locations", {}).items())
            salary_weights = sum(weight for _, weight in content_prefs.get("salary_ranges", {}).items())
            
            content_score = (category_weights + location_weights + salary_weights) / 3.0
        
        # Calculer le score d'interaction
        interaction_score = 0.0
        interaction_prefs = preferences.get("interaction_preferences", {})
        if interaction_prefs:
            # Utiliser le mode d'interaction comme indicateur
            if interaction_prefs.get("interaction_mode") == "direct":
                interaction_score = 0.8
            elif interaction_prefs.get("interaction_mode") == "visual":
                interaction_score = 0.6
            else:
                interaction_score = 0.4
        
        # Calculer le score de fonctionnalité
        feature_score = preferences.get("feature_preferences", {}).get("sophistication_score", 0.5)
        
        # Utiliser les poids de préférence de la configuration
        pref_weights = self.config["preference_weights"]
        global_score = (
            content_score * pref_weights["content_preferences"] + 
            interaction_score * pref_weights["interaction_preferences"] + 
            feature_score * pref_weights["feature_preferences"]
        ) / (pref_weights["content_preferences"] + pref_weights["interaction_preferences"] + pref_weights["feature_preferences"])
        
        # Combiner les scores
        return {
            "content_score": content_score,
            "interaction_score": interaction_score,
            "feature_score": feature_score,
            "global_score": global_score
        }
    
    def _normalize_scores(self, scores: Dict[str, float]) -> Dict[str, float]:
        """
        Normalise les scores pour qu'ils soient entre 0 et 1.
        
        Args:
            scores: Dictionnaire de scores
            
        Returns:
            Dictionnaire de scores normalisés
        """
        if not scores:
            return {}
            
        total = sum(scores.values())
        if total == 0:
            return {k: 0.0 for k in scores}
            
        return {k: v / total for k, v in scores.items()}
    
    def _extract_top_preferences(self, preferences: Dict[str, float], limit: int = 3) -> Dict[str, float]:
        """
        Extrait les top préférences d'un dictionnaire.
        
        Args:
            preferences: Dictionnaire de préférences avec scores
            limit: Nombre maximum de préférences à extraire
            
        Returns:
            Dictionnaire des top préférences
        """
        if not preferences:
            return {}
            
        sorted_prefs = sorted(preferences.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_prefs[:limit])
    
    def _get_item_features(self, item_id: str, item_type: str) -> Dict[str, Any]:
        """
        Récupère les caractéristiques d'un élément pour le calcul de recommandation.
        
        Args:
            item_id: Identifiant de l'élément
            item_type: Type de l'élément (job, cv, etc.)
            
        Returns:
            Dict contenant les caractéristiques de l'élément
        """
        # Dans un environnement réel, on récupérerait les caractéristiques depuis une base de données
        # Ici, on simule des caractéristiques pour le développement
        
        if item_type == "job":
            # Générer des caractéristiques aléatoires pour une offre d'emploi
            categories = ["engineering", "marketing", "sales", "design", "finance"]
            locations = ["paris", "lyon", "marseille", "bordeaux", "toulouse"]
            salary_ranges = ["30-45k", "45-60k", "60-80k", "80-100k", "100k+"]
            job_types = ["full-time", "part-time", "contract", "remote"]
            industries = ["tech", "healthcare", "finance", "retail", "education"]
            
            return {
                "id": item_id,
                "type": item_type,
                "category": np.random.choice(categories),
                "location": np.random.choice(locations),
                "salary_range": np.random.choice(salary_ranges),
                "job_type": np.random.choice(job_types),
                "industry": np.random.choice(industries),
                "skills": np.random.choice(["python", "javascript", "marketing", "sales", "design"], 
                                       size=np.random.randint(2, 5), replace=False).tolist()
            }
        elif item_type == "cv":
            # Générer des caractéristiques aléatoires pour un CV
            skills = ["python", "javascript", "marketing", "sales", "design", "management", "communication"]
            
            return {
                "id": item_id,
                "type": item_type,
                "skills": np.random.choice(skills, size=np.random.randint(3, 6), replace=False).tolist(),
                "experience_years": np.random.randint(1, 15),
                "education_level": np.random.choice(["bachelor", "master", "phd"])
            }
        else:
            # Type non reconnu
            return {}
    
    def _calculate_content_similarity(self, user_preferences: Dict[str, Any], 
                                    item_features: Dict[str, Any]) -> float:
        """
        Calcule la similarité entre les préférences de l'utilisateur et les caractéristiques d'un élément.
        
        Args:
            user_preferences: Préférences de contenu de l'utilisateur
            item_features: Caractéristiques de l'élément
            
        Returns:
            Score de similarité entre 0 et 1
        """
        if not user_preferences or not item_features:
            return 0.5  # Score neutre par défaut
        
        # Initialiser le score
        score = 0.0
        count = 0
        
        # Vérifier la correspondance pour la catégorie
        if "categories" in user_preferences and "category" in item_features:
            category = item_features["category"]
            if category in user_preferences["categories"]:
                score += user_preferences["categories"][category]
                count += 1
        
        # Vérifier la correspondance pour la localisation
        if "locations" in user_preferences and "location" in item_features:
            location = item_features["location"]
            if location in user_preferences["locations"]:
                score += user_preferences["locations"][location]
                count += 1
        
        # Vérifier la correspondance pour la plage de salaire
        if "salary_ranges" in user_preferences and "salary_range" in item_features:
            salary = item_features["salary_range"]
            if salary in user_preferences["salary_ranges"]:
                score += user_preferences["salary_ranges"][salary]
                count += 1
        
        # Vérifier la correspondance pour le type d'emploi
        if "job_types" in user_preferences and "job_type" in item_features:
            job_type = item_features["job_type"]
            if job_type in user_preferences["job_types"]:
                score += user_preferences["job_types"][job_type]
                count += 1
        
        # Vérifier la correspondance pour l'industrie
        if "industries" in user_preferences and "industry" in item_features:
            industry = item_features["industry"]
            if industry in user_preferences["industries"]:
                score += user_preferences["industries"][industry]
                count += 1
        
        # Vérifier la correspondance pour les compétences
        if "skills" in user_preferences and "skills" in item_features and isinstance(item_features["skills"], list):
            item_skills = set(item_features["skills"])
            skills_score = 0.0
            skills_count = 0
            
            for skill, weight in user_preferences["skills"].items():
                if skill in item_skills:
                    skills_score += weight
                    skills_count += 1
            
            if skills_count > 0:
                score += skills_score / skills_count
                count += 1
        
        # Calculer le score moyen
        if count > 0:
            return score / count
        else:
            return 0.5  # Score neutre par défaut
    
    def _save_preferences(self, user_id: str, preferences: Dict[str, Any]) -> None:
        """
        Sauvegarde les préférences calculées pour un utilisateur.
        
        Args:
            user_id: Identifiant de l'utilisateur
            preferences: Préférences calculées
        """
        # Mettre en cache
        self.preferences_cache[user_id] = preferences
        
        # Sauvegarder dans un fichier
        preferences_path = os.path.join(self.storage_path, f"user_{user_id}_preferences.json")
        try:
            with open(preferences_path, 'w') as file:
                json.dump(preferences, file, indent=2)
            logger.info(f"Saved preferences for user {user_id} to {preferences_path}")
        except Exception as e:
            logger.error(f"Failed to save preferences to file: {str(e)}")
