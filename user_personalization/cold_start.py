"""
Module de gestion du problème du cold start pour les nouveaux utilisateurs
"""

import json
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime
import random
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from user_personalization import (
    DEFAULT_WEIGHTS, 
    DEFAULT_DATABASE_URL, 
    COLD_START_PARAMS,
    logger
)

class ColdStartManager:
    """
    Gestionnaire du problème du cold start.
    
    Cette classe implémente des stratégies pour attribuer des profils
    initiaux aux nouveaux utilisateurs et assurer une transition progressive
    vers un profil personnalisé.
    """
    
    def __init__(self, db_url: Optional[str] = None):
        """
        Initialise le gestionnaire de cold start.
        
        Args:
            db_url: URL de connexion à la base de données.
                Si non spécifié, utilise la variable d'environnement DATABASE_URL.
        """
        self.db_url = db_url or DEFAULT_DATABASE_URL
        try:
            self.engine = create_engine(self.db_url)
            logger.info("Connexion à la base de données établie")
        except Exception as e:
            logger.error(f"Erreur de connexion à la base de données: {e}")
            self.engine = None
            
        # Paramètres de cold start
        self.exploration_rate = COLD_START_PARAMS.get('exploration_rate', 0.2)
        self.transition_factor = COLD_START_PARAMS.get('transition_factor', 0.1)
        self.min_interactions = COLD_START_PARAMS.get('min_interactions', 10)
        
        # Cache des profils de cold start
        self._profile_cache = None
    
    def get_cold_start_profile(self, user_id: int, user_data: Optional[Dict[str, Any]] = None) -> Dict[str, float]:
        """
        Détermine le profil cold start le plus adapté pour un nouvel utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            user_data: Données de l'utilisateur pour personnaliser le profil
            
        Returns:
            Dictionnaire des poids pour chaque critère de matching
        """
        # Calculer le nombre d'interactions de l'utilisateur
        interactions_count = self._get_interaction_count(user_id)
        
        # Si l'utilisateur a suffisamment d'interactions, il n'est plus dans la phase de cold start
        if interactions_count >= self.min_interactions:
            logger.debug(f"Utilisateur {user_id} n'est plus en phase de cold start ({interactions_count} interactions)")
            return {}
        
        # En phase de cold start, ajuster progressivement les poids en fonction du nombre d'interactions
        profile = self._select_best_profile(user_data)
        
        if not profile:
            logger.warning(f"Aucun profil cold start trouvé pour l'utilisateur {user_id}")
            return DEFAULT_WEIGHTS
        
        # Calculer le facteur de transition (0 au début, 1 à la fin de la phase de cold start)
        transition_progress = min(1.0, interactions_count / self.min_interactions)
        
        # Mélanger exploration (aléatoire) et exploitation (profil sélectionné)
        exploration_weight = self.exploration_rate * (1.0 - transition_progress)
        
        # Ajouter une composante aléatoire pour l'exploration
        if exploration_weight > 0:
            profile = self._add_exploration(profile, exploration_weight)
            
        logger.debug(f"Profil cold start pour l'utilisateur {user_id}: {profile}, progression: {transition_progress:.2f}")
        
        return profile
    
    def _select_best_profile(self, user_data: Optional[Dict[str, Any]] = None) -> Dict[str, float]:
        """
        Sélectionne le meilleur profil cold start en fonction des données utilisateur.
        
        Args:
            user_data: Données de l'utilisateur
            
        Returns:
            Profil cold start sélectionné
        """
        # Si aucune donnée utilisateur, utiliser le profil par défaut
        if not user_data:
            return self._get_default_profile()
        
        # Charger tous les profils si pas dans le cache
        if self._profile_cache is None:
            self._profile_cache = self._load_profiles()
            
        if not self._profile_cache:
            return DEFAULT_WEIGHTS
        
        # Évaluer chaque profil et trouver le meilleur
        best_profile = None
        best_score = -1
        
        for profile in self._profile_cache:
            score = self._evaluate_profile_match(profile, user_data)
            
            if score > best_score:
                best_score = score
                best_profile = profile
        
        if best_profile:
            # Extraire les poids
            weights = {
                'skills': best_profile.get('skills_weight', DEFAULT_WEIGHTS['skills']),
                'contract': best_profile.get('contract_weight', DEFAULT_WEIGHTS['contract']),
                'location': best_profile.get('location_weight', DEFAULT_WEIGHTS['location']),
                'date': best_profile.get('date_weight', DEFAULT_WEIGHTS['date']),
                'salary': best_profile.get('salary_weight', DEFAULT_WEIGHTS['salary']),
                'experience': best_profile.get('experience_weight', DEFAULT_WEIGHTS['experience']),
                'soft_skills': best_profile.get('soft_skills_weight', DEFAULT_WEIGHTS['soft_skills']),
                'culture': best_profile.get('culture_weight', DEFAULT_WEIGHTS['culture'])
            }
            return weights
        else:
            return self._get_default_profile()
    
    def _get_default_profile(self) -> Dict[str, float]:
        """
        Récupère le profil cold start par défaut.
        
        Returns:
            Profil par défaut
        """
        # Charger tous les profils si pas dans le cache
        if self._profile_cache is None:
            self._profile_cache = self._load_profiles()
            
        if not self._profile_cache:
            return DEFAULT_WEIGHTS
            
        # Chercher le profil nommé 'default'
        for profile in self._profile_cache:
            if profile.get('profile_name') == 'default':
                # Extraire les poids
                weights = {
                    'skills': profile.get('skills_weight', DEFAULT_WEIGHTS['skills']),
                    'contract': profile.get('contract_weight', DEFAULT_WEIGHTS['contract']),
                    'location': profile.get('location_weight', DEFAULT_WEIGHTS['location']),
                    'date': profile.get('date_weight', DEFAULT_WEIGHTS['date']),
                    'salary': profile.get('salary_weight', DEFAULT_WEIGHTS['salary']),
                    'experience': profile.get('experience_weight', DEFAULT_WEIGHTS['experience']),
                    'soft_skills': profile.get('soft_skills_weight', DEFAULT_WEIGHTS['soft_skills']),
                    'culture': profile.get('culture_weight', DEFAULT_WEIGHTS['culture'])
                }
                return weights
                
        # Si pas de profil par défaut, utiliser les poids par défaut
        return DEFAULT_WEIGHTS
    
    def _load_profiles(self) -> List[Dict[str, Any]]:
        """
        Charge tous les profils cold start depuis la base de données.
        
        Returns:
            Liste des profils
        """
        try:
            if self.engine is None:
                logger.warning("Connexion à la base de données non disponible")
                return []
                
            # Requête pour récupérer les profils
            query = """
            SELECT 
                id, profile_name, description, 
                skills_weight, contract_weight, location_weight, 
                date_weight, salary_weight, experience_weight,
                soft_skills_weight, culture_weight,
                conditions
            FROM cold_start_profiles
            WHERE active = TRUE
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                
                profiles = []
                for row in result:
                    profile = {
                        'id': row[0],
                        'profile_name': row[1],
                        'description': row[2],
                        'skills_weight': float(row[3]),
                        'contract_weight': float(row[4]),
                        'location_weight': float(row[5]),
                        'date_weight': float(row[6]),
                        'salary_weight': float(row[7]),
                        'experience_weight': float(row[8]),
                        'soft_skills_weight': float(row[9]),
                        'culture_weight': float(row[10]),
                        'conditions': json.loads(row[11]) if row[11] else {}
                    }
                    profiles.append(profile)
                
                logger.debug(f"Profils cold start chargés: {len(profiles)}")
                return profiles
        except Exception as e:
            logger.error(f"Erreur lors du chargement des profils cold start: {e}")
            return []
    
    def _evaluate_profile_match(self, profile: Dict[str, Any], user_data: Dict[str, Any]) -> float:
        """
        Évalue à quel point un profil correspond aux données utilisateur.
        
        Args:
            profile: Profil à évaluer
            user_data: Données de l'utilisateur
            
        Returns:
            Score de correspondance (0-1)
        """
        conditions = profile.get('conditions', {})
        if not conditions:
            return 0.5  # Profil générique
            
        # Évaluer chaque condition
        matches = 0
        total_conditions = 0
        
        for key, value in conditions.items():
            if key in user_data:
                total_conditions += 1
                
                # Différents types de comparaisons
                if isinstance(value, (str, bool)) and user_data[key] == value:
                    matches += 1
                elif isinstance(value, (int, float)):
                    # Intervalles de valeurs
                    if key.endswith('_min') and float(user_data.get(key.replace('_min', ''), 0)) >= value:
                        matches += 1
                    elif key.endswith('_max') and float(user_data.get(key.replace('_max', ''), 0)) <= value:
                        matches += 1
                    elif user_data[key] == value:
                        matches += 1
                elif isinstance(value, list) and user_data[key] in value:
                    matches += 1
        
        # Calculer le score de correspondance
        if total_conditions == 0:
            return 0.5
        
        return matches / total_conditions
    
    def _add_exploration(self, profile: Dict[str, float], exploration_weight: float) -> Dict[str, float]:
        """
        Ajoute une composante d'exploration au profil.
        
        Args:
            profile: Profil cold start
            exploration_weight: Poids de l'exploration (0-1)
            
        Returns:
            Profil ajusté avec exploration
        """
        # Générer des poids aléatoires
        random_weights = {
            'skills': random.uniform(0.1, 0.5),
            'contract': random.uniform(0.05, 0.25),
            'location': random.uniform(0.1, 0.3),
            'date': random.uniform(0.05, 0.2),
            'salary': random.uniform(0.1, 0.3),
            'experience': random.uniform(0.05, 0.25),
            'soft_skills': random.uniform(0, 0.1),
            'culture': random.uniform(0, 0.1)
        }
        
        # Normaliser les poids aléatoires
        total = sum(random_weights.values())
        for key in random_weights:
            random_weights[key] /= total
        
        # Mélanger les poids du profil et aléatoires
        mixed_weights = {}
        for key in profile:
            mixed_weights[key] = profile[key] * (1 - exploration_weight) + random_weights[key] * exploration_weight
        
        # Normaliser le résultat
        total = sum(mixed_weights.values())
        for key in mixed_weights:
            mixed_weights[key] /= total
        
        return mixed_weights
    
    def _get_interaction_count(self, user_id: int) -> int:
        """
        Compte le nombre d'interactions d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Nombre d'interactions
        """
        try:
            if self.engine is None:
                logger.warning("Connexion à la base de données non disponible")
                return 0
                
            # Requête pour compter les interactions (feedbacks et événements)
            query = """
            SELECT COUNT(*) FROM (
                SELECT user_id FROM personalization_feedback 
                WHERE user_id = :user_id
                
                UNION ALL
                
                SELECT user_id FROM tracking_events
                WHERE user_id = :user_id
            ) AS interactions
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(query), {"user_id": user_id})
                count = result.scalar()
                
                return count or 0
        except Exception as e:
            logger.error(f"Erreur lors du comptage des interactions: {e}")
            return 0
    
    def create_profile(self, profile_data: Dict[str, Any]) -> bool:
        """
        Crée un nouveau profil cold start.
        
        Args:
            profile_data: Données du profil
            
        Returns:
            True si la création a réussi, False sinon
        """
        try:
            if self.engine is None:
                logger.warning("Connexion à la base de données non disponible")
                return False
                
            # Valider les données obligatoires
            if 'profile_name' not in profile_data:
                logger.error("Le nom du profil est obligatoire")
                return False
                
            # Extraire les données du profil
            profile_name = profile_data.get('profile_name')
            description = profile_data.get('description', '')
            conditions = profile_data.get('conditions', {})
            
            # Extraire les poids avec valeurs par défaut
            weights = {
                'skills_weight': profile_data.get('weights', {}).get('skills', DEFAULT_WEIGHTS['skills']),
                'contract_weight': profile_data.get('weights', {}).get('contract', DEFAULT_WEIGHTS['contract']),
                'location_weight': profile_data.get('weights', {}).get('location', DEFAULT_WEIGHTS['location']),
                'date_weight': profile_data.get('weights', {}).get('date', DEFAULT_WEIGHTS['date']),
                'salary_weight': profile_data.get('weights', {}).get('salary', DEFAULT_WEIGHTS['salary']),
                'experience_weight': profile_data.get('weights', {}).get('experience', DEFAULT_WEIGHTS['experience']),
                'soft_skills_weight': profile_data.get('weights', {}).get('soft_skills', DEFAULT_WEIGHTS['soft_skills']),
                'culture_weight': profile_data.get('weights', {}).get('culture', DEFAULT_WEIGHTS['culture'])
            }
            
            # Requête pour insérer le profil
            query = """
            INSERT INTO cold_start_profiles (
                profile_name, description, 
                skills_weight, contract_weight, location_weight, 
                date_weight, salary_weight, experience_weight,
                soft_skills_weight, culture_weight,
                conditions, active
            ) VALUES (
                :profile_name, :description, 
                :skills_weight, :contract_weight, :location_weight, 
                :date_weight, :salary_weight, :experience_weight,
                :soft_skills_weight, :culture_weight,
                :conditions, TRUE
            )
            ON CONFLICT (profile_name) DO UPDATE
            SET 
                description = :description,
                skills_weight = :skills_weight,
                contract_weight = :contract_weight,
                location_weight = :location_weight,
                date_weight = :date_weight,
                salary_weight = :salary_weight,
                experience_weight = :experience_weight,
                soft_skills_weight = :soft_skills_weight,
                culture_weight = :culture_weight,
                conditions = :conditions
            """
            
            with self.engine.connect() as conn:
                conn.execute(text(query), {
                    "profile_name": profile_name,
                    "description": description,
                    "skills_weight": weights['skills_weight'],
                    "contract_weight": weights['contract_weight'],
                    "location_weight": weights['location_weight'],
                    "date_weight": weights['date_weight'],
                    "salary_weight": weights['salary_weight'],
                    "experience_weight": weights['experience_weight'],
                    "soft_skills_weight": weights['soft_skills_weight'],
                    "culture_weight": weights['culture_weight'],
                    "conditions": json.dumps(conditions)
                })
                
                conn.commit()
            
            # Vider le cache
            self._profile_cache = None
            
            logger.info(f"Profil cold start '{profile_name}' créé")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la création du profil cold start: {e}")
            return False
    
    def get_all_profiles(self) -> List[Dict[str, Any]]:
        """
        Récupère tous les profils cold start.
        
        Returns:
            Liste des profils
        """
        profiles = self._load_profiles()
        
        # Reformater les profils pour l'API
        formatted_profiles = []
        for profile in profiles:
            weights = {
                'skills': profile.get('skills_weight'),
                'contract': profile.get('contract_weight'),
                'location': profile.get('location_weight'),
                'date': profile.get('date_weight'),
                'salary': profile.get('salary_weight'),
                'experience': profile.get('experience_weight'),
                'soft_skills': profile.get('soft_skills_weight'),
                'culture': profile.get('culture_weight')
            }
            
            formatted_profiles.append({
                'id': profile.get('id'),
                'name': profile.get('profile_name'),
                'description': profile.get('description'),
                'weights': weights,
                'conditions': profile.get('conditions', {})
            })
        
        return formatted_profiles
    
    def delete_profile(self, profile_id: int) -> bool:
        """
        Supprime un profil cold start.
        
        Args:
            profile_id: ID du profil
            
        Returns:
            True si la suppression a réussi, False sinon
        """
        try:
            if self.engine is None:
                logger.warning("Connexion à la base de données non disponible")
                return False
                
            # Ne pas supprimer le profil par défaut
            check_query = """
            SELECT profile_name FROM cold_start_profiles
            WHERE id = :profile_id
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(check_query), {"profile_id": profile_id})
                profile_name = result.scalar()
                
                if profile_name == 'default':
                    logger.warning("Impossible de supprimer le profil par défaut")
                    return False
                
                # Requête pour supprimer le profil
                query = """
                DELETE FROM cold_start_profiles
                WHERE id = :profile_id
                """
                
                conn.execute(text(query), {"profile_id": profile_id})
                conn.commit()
            
            # Vider le cache
            self._profile_cache = None
            
            logger.info(f"Profil cold start {profile_id} supprimé")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du profil cold start: {e}")
            return False
