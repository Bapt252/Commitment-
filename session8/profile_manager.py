"""
Gestionnaire de profils utilisateurs.

Ce module est responsable de la création, mise à jour et gestion des profils utilisateurs
basés sur les caractéristiques comportementales extraites par le FeatureExtractor.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import os

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class ProfileManager:
    """
    Gestionnaire de profils utilisateurs qui maintient et actualise les profils
    comportementaux des utilisateurs.
    """
    
    def __init__(self, storage_path: str = "./profiles", db_connector=None):
        """
        Initialise le gestionnaire de profils.
        
        Args:
            storage_path: Chemin vers le dossier de stockage des profils
            db_connector: Connecteur vers la base de données (optionnel)
        """
        self.storage_path = storage_path
        self.db_connector = db_connector
        
        # Créer le dossier de stockage s'il n'existe pas
        os.makedirs(storage_path, exist_ok=True)
        
        # Dictionnaire pour mettre en cache les profils fréquemment consultés
        self.profile_cache = {}
        
        # Définir la structure du profil
        self.profile_schema = {
            "base_info": {},
            "behavioral_features": {},
            "preferences": {},
            "segments": [],
            "predictions": {},
            "history": []
        }
        
        logger.info(f"ProfileManager initialized with storage path: {storage_path}")
    
    def get_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Récupère le profil complet d'un utilisateur.
        
        Args:
            user_id: Identifiant de l'utilisateur
            
        Returns:
            Profil utilisateur complet
        """
        # Vérifier le cache d'abord
        if user_id in self.profile_cache:
            logger.info(f"Returning cached profile for user {user_id}")
            return self.profile_cache[user_id]
        
        # Essayer de récupérer depuis la base de données si un connecteur est disponible
        if self.db_connector:
            try:
                query = f"SELECT profile_data FROM user_profiles WHERE user_id = '{user_id}'"
                result = self.db_connector.execute_query(query)
                if result and len(result) > 0:
                    profile_data = result[0]["profile_data"]
                    profile = json.loads(profile_data)
                    
                    # Mise en cache pour accès ultérieur
                    self.profile_cache[user_id] = profile
                    logger.info(f"Retrieved profile from database for user {user_id}")
                    return profile
            except Exception as e:
                logger.error(f"Failed to retrieve profile from database: {str(e)}")
        
        # Sinon, essayer de charger depuis le stockage de fichiers
        profile_path = os.path.join(self.storage_path, f"{user_id}.json")
        if os.path.exists(profile_path):
            try:
                with open(profile_path, 'r') as file:
                    profile = json.load(file)
                    
                # Mise en cache pour accès ultérieur
                self.profile_cache[user_id] = profile
                logger.info(f"Retrieved profile from file storage for user {user_id}")
                return profile
            except Exception as e:
                logger.error(f"Failed to load profile from file: {str(e)}")
        
        # Si le profil n'existe pas, créer un nouveau
        logger.info(f"Creating new profile for user {user_id}")
        return self.create_profile(user_id)
    
    def create_profile(self, user_id: str, base_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Crée un nouveau profil utilisateur.
        
        Args:
            user_id: Identifiant de l'utilisateur
            base_info: Informations de base sur l'utilisateur (optionnel)
            
        Returns:
            Nouveau profil utilisateur
        """
        # Créer un profil de base à partir du schéma
        profile = self.profile_schema.copy()
        
        # Ajouter l'ID utilisateur et les informations de base
        profile["user_id"] = user_id
        profile["creation_date"] = datetime.now().isoformat()
        profile["last_updated"] = profile["creation_date"]
        
        # Ajouter les informations de base si fournies
        if base_info:
            profile["base_info"] = base_info
        
        # Initialiser un historique vide
        profile["history"] = []
        
        # Sauvegarder le nouveau profil
        self._save_profile(user_id, profile)
        logger.info(f"Created new profile for user {user_id}")
        
        return profile
    
    def update_profile(self, user_id: str, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Met à jour le profil d'un utilisateur avec de nouvelles caractéristiques comportementales.
        
        Args:
            user_id: Identifiant de l'utilisateur
            features: Nouvelles caractéristiques comportementales
            
        Returns:
            Profil utilisateur mis à jour
        """
        # Récupérer le profil actuel
        profile = self.get_profile(user_id)
        
        # Sauvegarder l'état actuel des caractéristiques dans l'historique
        if "behavioral_features" in profile and profile["behavioral_features"]:
            history_entry = {
                "timestamp": profile.get("last_updated", datetime.now().isoformat()),
                "behavioral_features": profile["behavioral_features"].copy()
            }
            profile["history"].append(history_entry)
            
            # Limiter la taille de l'historique à 10 entrées
            if len(profile["history"]) > 10:
                profile["history"] = profile["history"][-10:]
        
        # Mettre à jour les caractéristiques comportementales
        profile["behavioral_features"] = features
        
        # Mettre à jour la date de dernière modification
        profile["last_updated"] = datetime.now().isoformat()
        
        # Sauvegarder le profil mis à jour
        self._save_profile(user_id, profile)
        logger.info(f"Updated profile for user {user_id} with new features")
        
        return profile
    
    def update_base_info(self, user_id: str, base_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Met à jour les informations de base d'un profil utilisateur.
        
        Args:
            user_id: Identifiant de l'utilisateur
            base_info: Nouvelles informations de base
            
        Returns:
            Profil utilisateur mis à jour
        """
        # Récupérer le profil actuel
        profile = self.get_profile(user_id)
        
        # Mettre à jour les informations de base
        profile["base_info"].update(base_info)
        
        # Mettre à jour la date de dernière modification
        profile["last_updated"] = datetime.now().isoformat()
        
        # Sauvegarder le profil mis à jour
        self._save_profile(user_id, profile)
        logger.info(f"Updated base info for user {user_id}")
        
        return profile
    
    def update_preferences(self, user_id: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Met à jour les préférences d'un profil utilisateur.
        
        Args:
            user_id: Identifiant de l'utilisateur
            preferences: Nouvelles préférences
            
        Returns:
            Profil utilisateur mis à jour
        """
        # Récupérer le profil actuel
        profile = self.get_profile(user_id)
        
        # Mettre à jour les préférences
        profile["preferences"].update(preferences)
        
        # Mettre à jour la date de dernière modification
        profile["last_updated"] = datetime.now().isoformat()
        
        # Sauvegarder le profil mis à jour
        self._save_profile(user_id, profile)
        logger.info(f"Updated preferences for user {user_id}")
        
        return profile
    
    def update_segments(self, user_id: str, segments: List[str]) -> Dict[str, Any]:
        """
        Met à jour les segments d'un profil utilisateur.
        
        Args:
            user_id: Identifiant de l'utilisateur
            segments: Nouveaux segments
            
        Returns:
            Profil utilisateur mis à jour
        """
        # Récupérer le profil actuel
        profile = self.get_profile(user_id)
        
        # Mettre à jour les segments
        profile["segments"] = segments
        
        # Mettre à jour la date de dernière modification
        profile["last_updated"] = datetime.now().isoformat()
        
        # Sauvegarder le profil mis à jour
        self._save_profile(user_id, profile)
        logger.info(f"Updated segments for user {user_id}: {segments}")
        
        return profile
    
    def update_predictions(self, user_id: str, predictions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Met à jour les prédictions pour un profil utilisateur.
        
        Args:
            user_id: Identifiant de l'utilisateur
            predictions: Nouvelles prédictions
            
        Returns:
            Profil utilisateur mis à jour
        """
        # Récupérer le profil actuel
        profile = self.get_profile(user_id)
        
        # Mettre à jour les prédictions
        profile["predictions"].update(predictions)
        
        # Mettre à jour la date de dernière modification
        profile["last_updated"] = datetime.now().isoformat()
        
        # Sauvegarder le profil mis à jour
        self._save_profile(user_id, profile)
        logger.info(f"Updated predictions for user {user_id}")
        
        return profile
    
    def get_feature_history(self, user_id: str, feature_name: str) -> List[Tuple[str, Any]]:
        """
        Récupère l'historique d'une caractéristique spécifique.
        
        Args:
            user_id: Identifiant de l'utilisateur
            feature_name: Nom de la caractéristique
            
        Returns:
            Liste de tuples (timestamp, valeur) pour la caractéristique
        """
        # Récupérer le profil
        profile = self.get_profile(user_id)
        
        # Extraire l'historique de la caractéristique spécifique
        feature_history = []
        
        # Ajouter la valeur actuelle
        current_value = profile.get("behavioral_features", {}).get(feature_name)
        if current_value is not None:
            feature_history.append((profile.get("last_updated"), current_value))
        
        # Parcourir l'historique
        for entry in profile.get("history", []):
            timestamp = entry.get("timestamp")
            value = entry.get("behavioral_features", {}).get(feature_name)
            if timestamp and value is not None:
                feature_history.append((timestamp, value))
        
        # Trier par timestamp (du plus récent au plus ancien)
        feature_history.sort(key=lambda x: x[0], reverse=True)
        
        return feature_history
    
    def delete_profile(self, user_id: str) -> bool:
        """
        Supprime le profil d'un utilisateur (conformité RGPD).
        
        Args:
            user_id: Identifiant de l'utilisateur
            
        Returns:
            True si la suppression a réussi, False sinon
        """
        # Supprimer du cache
        if user_id in self.profile_cache:
            del self.profile_cache[user_id]
        
        # Supprimer de la base de données si un connecteur est disponible
        success_db = True
        if self.db_connector:
            try:
                query = f"DELETE FROM user_profiles WHERE user_id = '{user_id}'"
                self.db_connector.execute_query(query)
                logger.info(f"Deleted profile from database for user {user_id}")
            except Exception as e:
                logger.error(f"Failed to delete profile from database: {str(e)}")
                success_db = False
        
        # Supprimer du stockage de fichiers
        success_file = True
        profile_path = os.path.join(self.storage_path, f"{user_id}.json")
        if os.path.exists(profile_path):
            try:
                os.remove(profile_path)
                logger.info(f"Deleted profile from file storage for user {user_id}")
            except Exception as e:
                logger.error(f"Failed to delete profile file: {str(e)}")
                success_file = False
        
        return success_db and success_file
    
    def export_profile(self, user_id: str, format: str = "json") -> str:
        """
        Exporte le profil d'un utilisateur dans un format spécifique (conformité RGPD).
        
        Args:
            user_id: Identifiant de l'utilisateur
            format: Format d'exportation (json, csv, etc.)
            
        Returns:
            Profil exporté dans le format spécifié
        """
        profile = self.get_profile(user_id)
        
        if format.lower() == "json":
            return json.dumps(profile, indent=2)
        else:
            logger.warning(f"Export format '{format}' not supported, defaulting to JSON")
            return json.dumps(profile, indent=2)
    
    def get_all_profiles(self) -> List[Dict[str, Any]]:
        """
        Récupère tous les profils utilisateurs.
        
        Returns:
            Liste de tous les profils utilisateurs
        """
        profiles = []
        
        # Si un connecteur est disponible, récupérer depuis la base de données
        if self.db_connector:
            try:
                query = "SELECT profile_data FROM user_profiles"
                results = self.db_connector.execute_query(query)
                if results:
                    for result in results:
                        profile_data = result["profile_data"]
                        profile = json.loads(profile_data)
                        profiles.append(profile)
                    logger.info(f"Retrieved {len(profiles)} profiles from database")
                    return profiles
            except Exception as e:
                logger.error(f"Failed to retrieve profiles from database: {str(e)}")
        
        # Sinon, récupérer depuis le stockage de fichiers
        try:
            for filename in os.listdir(self.storage_path):
                if filename.endswith(".json"):
                    file_path = os.path.join(self.storage_path, filename)
                    with open(file_path, 'r') as file:
                        profile = json.load(file)
                        profiles.append(profile)
            logger.info(f"Retrieved {len(profiles)} profiles from file storage")
        except Exception as e:
            logger.error(f"Failed to retrieve profiles from file storage: {str(e)}")
        
        return profiles
    
    def _save_profile(self, user_id: str, profile: Dict[str, Any]) -> bool:
        """
        Sauvegarde un profil utilisateur.
        
        Args:
            user_id: Identifiant de l'utilisateur
            profile: Profil utilisateur à sauvegarder
            
        Returns:
            True si la sauvegarde a réussi, False sinon
        """
        # Mettre à jour le cache
        self.profile_cache[user_id] = profile
        
        # Sauvegarder dans la base de données si un connecteur est disponible
        success_db = True
        if self.db_connector:
            try:
                profile_data = json.dumps(profile)
                query = f"""
                INSERT INTO user_profiles (user_id, profile_data) 
                VALUES ('{user_id}', '{profile_data}')
                ON CONFLICT (user_id) 
                DO UPDATE SET profile_data = '{profile_data}'
                """
                self.db_connector.execute_query(query)
                logger.info(f"Saved profile to database for user {user_id}")
            except Exception as e:
                logger.error(f"Failed to save profile to database: {str(e)}")
                success_db = False
        
        # Sauvegarder dans le stockage de fichiers
        success_file = True
        profile_path = os.path.join(self.storage_path, f"{user_id}.json")
        try:
            with open(profile_path, 'w') as file:
                json.dump(profile, file, indent=2)
            logger.info(f"Saved profile to file storage for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to save profile to file: {str(e)}")
            success_file = False
        
        return success_db and success_file
    
    def clear_cache(self) -> None:
        """
        Vide le cache des profils pour libérer de la mémoire.
        """
        self.profile_cache.clear()
        logger.info("Profile cache cleared")
