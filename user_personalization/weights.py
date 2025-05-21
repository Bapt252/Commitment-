"""
Module de gestion des poids personnalisés par utilisateur
"""

import json
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from user_personalization import DEFAULT_WEIGHTS, DEFAULT_DATABASE_URL, logger

class UserWeightsManager:
    """
    Gestionnaire des poids de matching personnalisés par utilisateur.
    
    Cette classe permet de stocker, récupérer et mettre à jour les poids
    utilisés pour le matching pour chaque utilisateur individuellement.
    """
    
    def __init__(self, db_url: Optional[str] = None):
        """
        Initialise le gestionnaire de poids utilisateur.
        
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
            
        # Cache pour éviter de faire trop de requêtes
        self._cache = {}
        
    def get_user_weights(self, user_id: int) -> Dict[str, float]:
        """
        Récupère les poids de matching pour un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Dictionnaire des poids pour chaque critère de matching
        """
        # Vérifier si les poids sont dans le cache
        if user_id in self._cache:
            logger.debug(f"Poids pour l'utilisateur {user_id} trouvés dans le cache")
            return self._cache[user_id]
            
        try:
            if self.engine is None:
                logger.warning("Connexion à la base de données non disponible, utilisation des poids par défaut")
                return DEFAULT_WEIGHTS
                
            # Requête pour récupérer les poids
            query = """
            SELECT 
                skills_weight, contract_weight, location_weight, 
                date_weight, salary_weight, experience_weight,
                soft_skills_weight, culture_weight
            FROM user_matching_weights
            WHERE user_id = :user_id
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(query), {"user_id": user_id})
                row = result.fetchone()
                
                if row:
                    # Récupérer les poids depuis la base de données
                    weights = {
                        'skills': float(row[0]),
                        'contract': float(row[1]),
                        'location': float(row[2]),
                        'date': float(row[3]),
                        'salary': float(row[4]),
                        'experience': float(row[5]),
                        'soft_skills': float(row[6]),
                        'culture': float(row[7])
                    }
                    
                    # Mettre à jour le cache
                    self._cache[user_id] = weights
                    logger.debug(f"Poids pour l'utilisateur {user_id} récupérés depuis la base de données")
                    return weights
                else:
                    # Si l'utilisateur n'a pas de poids personnalisés, utiliser les poids par défaut
                    logger.debug(f"Aucun poids personnalisé trouvé pour l'utilisateur {user_id}, utilisation des poids par défaut")
                    
                    # Stocker les poids par défaut pour cet utilisateur
                    self.set_user_weights(user_id, DEFAULT_WEIGHTS, source='system')
                    
                    # Mettre à jour le cache
                    self._cache[user_id] = DEFAULT_WEIGHTS
                    return DEFAULT_WEIGHTS
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des poids: {e}")
            return DEFAULT_WEIGHTS
            
    def set_user_weights(self, user_id: int, weights: Dict[str, float], 
                         source: str = 'user') -> bool:
        """
        Définit les poids de matching pour un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            weights: Dictionnaire des poids pour chaque critère
            source: Source de la mise à jour ('user', 'system', 'ab_test', etc.)
            
        Returns:
            True si la mise à jour a réussi, False sinon
        """
        try:
            if self.engine is None:
                logger.warning("Connexion à la base de données non disponible, impossible de sauvegarder les poids")
                return False
                
            # Normaliser les poids (somme = 1)
            normalized_weights = self._normalize_weights(weights)
            
            # Vérifier si des poids existent déjà pour cet utilisateur
            check_query = """
            SELECT id FROM user_matching_weights
            WHERE user_id = :user_id
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(check_query), {"user_id": user_id})
                existing = result.fetchone()
                
                if existing:
                    # Mettre à jour les poids existants
                    update_query = """
                    UPDATE user_matching_weights
                    SET 
                        skills_weight = :skills,
                        contract_weight = :contract,
                        location_weight = :location,
                        date_weight = :date,
                        salary_weight = :salary,
                        experience_weight = :experience,
                        soft_skills_weight = :soft_skills,
                        culture_weight = :culture,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = :user_id
                    """
                    
                    conn.execute(text(update_query), {
                        "user_id": user_id,
                        "skills": normalized_weights.get('skills', DEFAULT_WEIGHTS['skills']),
                        "contract": normalized_weights.get('contract', DEFAULT_WEIGHTS['contract']),
                        "location": normalized_weights.get('location', DEFAULT_WEIGHTS['location']),
                        "date": normalized_weights.get('date', DEFAULT_WEIGHTS['date']),
                        "salary": normalized_weights.get('salary', DEFAULT_WEIGHTS['salary']),
                        "experience": normalized_weights.get('experience', DEFAULT_WEIGHTS['experience']),
                        "soft_skills": normalized_weights.get('soft_skills', DEFAULT_WEIGHTS['soft_skills']),
                        "culture": normalized_weights.get('culture', DEFAULT_WEIGHTS['culture'])
                    })
                else:
                    # Créer de nouveaux poids
                    insert_query = """
                    INSERT INTO user_matching_weights (
                        user_id, skills_weight, contract_weight, 
                        location_weight, date_weight, salary_weight, 
                        experience_weight, soft_skills_weight, culture_weight
                    ) VALUES (
                        :user_id, :skills, :contract, :location, 
                        :date, :salary, :experience, :soft_skills, :culture
                    )
                    """
                    
                    conn.execute(text(insert_query), {
                        "user_id": user_id,
                        "skills": normalized_weights.get('skills', DEFAULT_WEIGHTS['skills']),
                        "contract": normalized_weights.get('contract', DEFAULT_WEIGHTS['contract']),
                        "location": normalized_weights.get('location', DEFAULT_WEIGHTS['location']),
                        "date": normalized_weights.get('date', DEFAULT_WEIGHTS['date']),
                        "salary": normalized_weights.get('salary', DEFAULT_WEIGHTS['salary']),
                        "experience": normalized_weights.get('experience', DEFAULT_WEIGHTS['experience']),
                        "soft_skills": normalized_weights.get('soft_skills', DEFAULT_WEIGHTS['soft_skills']),
                        "culture": normalized_weights.get('culture', DEFAULT_WEIGHTS['culture'])
                    })
                
                # Enregistrer l'historique des poids
                history_query = """
                INSERT INTO user_matching_weights_history (
                    user_id, skills_weight, contract_weight, 
                    location_weight, date_weight, salary_weight, 
                    experience_weight, soft_skills_weight, 
                    culture_weight, source
                ) VALUES (
                    :user_id, :skills, :contract, :location, 
                    :date, :salary, :experience, :soft_skills, 
                    :culture, :source
                )
                """
                
                conn.execute(text(history_query), {
                    "user_id": user_id,
                    "skills": normalized_weights.get('skills', DEFAULT_WEIGHTS['skills']),
                    "contract": normalized_weights.get('contract', DEFAULT_WEIGHTS['contract']),
                    "location": normalized_weights.get('location', DEFAULT_WEIGHTS['location']),
                    "date": normalized_weights.get('date', DEFAULT_WEIGHTS['date']),
                    "salary": normalized_weights.get('salary', DEFAULT_WEIGHTS['salary']),
                    "experience": normalized_weights.get('experience', DEFAULT_WEIGHTS['experience']),
                    "soft_skills": normalized_weights.get('soft_skills', DEFAULT_WEIGHTS['soft_skills']),
                    "culture": normalized_weights.get('culture', DEFAULT_WEIGHTS['culture']),
                    "source": source
                })
                
                conn.commit()
            
            # Mettre à jour le cache
            self._cache[user_id] = normalized_weights
            logger.info(f"Poids pour l'utilisateur {user_id} mis à jour (source: {source})")
            
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des poids: {e}")
            return False
            
    def adjust_weights_from_feedback(self, user_id: int, 
                                    feedback_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Ajuste les poids en fonction du feedback utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            feedback_data: Données de feedback (rating, critère préféré, etc.)
            
        Returns:
            Nouveaux poids après ajustement
        """
        # Récupérer les poids actuels
        current_weights = self.get_user_weights(user_id)
        
        # Initialiser les nouveaux poids
        new_weights = current_weights.copy()
        
        # Facteur d'ajustement (plus petit = changements plus progressifs)
        adjustment_factor = 0.1
        
        # Critère préféré s'il est spécifié
        if 'preferred_criterion' in feedback_data and feedback_data['preferred_criterion'] in new_weights:
            preferred = feedback_data['preferred_criterion']
            
            # Augmenter le poids du critère préféré
            new_weights[preferred] = new_weights[preferred] + adjustment_factor
            
            # Réduire proportionnellement les autres poids
            reduction_factor = adjustment_factor / (len(new_weights) - 1)
            for criterion in new_weights:
                if criterion != preferred:
                    new_weights[criterion] = max(0.0, new_weights[criterion] - reduction_factor)
        
        # Si un rating est fourni, ajuster en fonction de la satisfaction
        if 'rating' in feedback_data and isinstance(feedback_data['rating'], (int, float)):
            rating = float(feedback_data['rating'])
            
            # Si le rating est élevé (4-5 sur 5), renforcer les poids actuels
            if rating >= 4.0:
                # Les poids actuels semblent bien fonctionner, les renforcer légèrement
                pass
            # Si le rating est faible (1-2 sur 5), ajuster vers une distribution plus équilibrée
            elif rating <= 2.0:
                # Les poids actuels ne fonctionnent pas bien, les ajuster vers la moyenne
                for criterion in new_weights:
                    target = DEFAULT_WEIGHTS[criterion]
                    new_weights[criterion] = new_weights[criterion] * (1 - adjustment_factor) + target * adjustment_factor
        
        # Normaliser les poids
        normalized_weights = self._normalize_weights(new_weights)
        
        # Sauvegarder les nouveaux poids
        self.set_user_weights(user_id, normalized_weights, source='feedback')
        
        return normalized_weights
    
    def get_weight_history(self, user_id: int, 
                          limit: int = 10) -> List[Dict[str, Any]]:
        """
        Récupère l'historique des modifications de poids pour un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            limit: Nombre maximum d'entrées à récupérer
            
        Returns:
            Liste des modifications de poids
        """
        try:
            if self.engine is None:
                logger.warning("Connexion à la base de données non disponible")
                return []
                
            # Requête pour récupérer l'historique
            query = """
            SELECT 
                skills_weight, contract_weight, location_weight, 
                date_weight, salary_weight, experience_weight,
                soft_skills_weight, culture_weight,
                source, created_at
            FROM user_matching_weights_history
            WHERE user_id = :user_id
            ORDER BY created_at DESC
            LIMIT :limit
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(query), {
                    "user_id": user_id,
                    "limit": limit
                })
                
                history = []
                for row in result:
                    history.append({
                        'skills': float(row[0]),
                        'contract': float(row[1]),
                        'location': float(row[2]),
                        'date': float(row[3]),
                        'salary': float(row[4]),
                        'experience': float(row[5]),
                        'soft_skills': float(row[6]),
                        'culture': float(row[7]),
                        'source': row[8],
                        'created_at': row[9].isoformat() if row[9] else None
                    })
                
                return history
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'historique des poids: {e}")
            return []
    
    def _normalize_weights(self, weights: Dict[str, float]) -> Dict[str, float]:
        """
        Normalise les poids pour que leur somme soit égale à 1.
        
        Args:
            weights: Dictionnaire des poids
            
        Returns:
            Dictionnaire des poids normalisés
        """
        # Vérifier si les poids sont valides
        if not weights:
            return DEFAULT_WEIGHTS
            
        # Calculer la somme des poids
        weight_sum = sum(weights.values())
        
        # Si la somme est 0, utiliser les poids par défaut
        if weight_sum == 0:
            return DEFAULT_WEIGHTS
            
        # Normaliser les poids
        normalized = {k: v / weight_sum for k, v in weights.items()}
        
        return normalized
            
    def clear_cache(self, user_id: Optional[int] = None):
        """
        Vide le cache des poids.
        
        Args:
            user_id: ID de l'utilisateur. Si None, vide tout le cache.
        """
        if user_id is None:
            self._cache = {}
            logger.debug("Cache des poids vidé")
        else:
            if user_id in self._cache:
                del self._cache[user_id]
                logger.debug(f"Cache des poids pour l'utilisateur {user_id} vidé")
