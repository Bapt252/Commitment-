"""
Module de gestion des préférences temporelles pour la personnalisation
"""

import json
import logging
import math
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from user_personalization import (
    DEFAULT_WEIGHTS, 
    DEFAULT_DATABASE_URL, 
    TEMPORAL_PARAMS,
    logger
)

class TemporalPreferencesManager:
    """
    Gestionnaire des préférences temporelles des utilisateurs.
    
    Cette classe permet de détecter et d'adapter les poids aux changements
    de préférences des utilisateurs au fil du temps.
    """
    
    def __init__(self, db_url: Optional[str] = None):
        """
        Initialise le gestionnaire de préférences temporelles.
        
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
            
        # Paramètres temporels
        self.recency_factor = TEMPORAL_PARAMS.get('recency_factor', 0.8)
        self.half_life_days = TEMPORAL_PARAMS.get('half_life_days', 30)
    
    def apply_temporal_weights(self, user_id: int, base_weights: Dict[str, float]) -> Dict[str, float]:
        """
        Applique une pondération temporelle aux poids de base.
        
        Cette méthode ajuste les poids en fonction des préférences récentes de l'utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            base_weights: Poids de base à ajuster
            
        Returns:
            Poids ajustés avec la composante temporelle
        """
        # Récupérer les paramètres temporels de l'utilisateur
        params = self.get_user_temporal_params(user_id)
        
        # Si pas de paramètres spécifiques, utiliser les paramètres par défaut
        if not params:
            recency_factor = self.recency_factor
        else:
            recency_factor = params.get('recency_factor', self.recency_factor)
        
        # Si le facteur de récence est très faible, retourner les poids de base
        if recency_factor < 0.1:
            return base_weights
        
        # Récupérer les poids récents basés sur l'activité
        recent_weights = self._calculate_recent_weights(user_id)
        
        if not recent_weights:
            return base_weights
        
        # Mélanger les poids de base et récents
        adjusted_weights = {}
        for key in base_weights:
            if key in recent_weights:
                adjusted_weights[key] = (
                    base_weights[key] * (1 - recency_factor) + 
                    recent_weights[key] * recency_factor
                )
            else:
                adjusted_weights[key] = base_weights[key]
        
        # Normaliser les poids
        total = sum(adjusted_weights.values())
        for key in adjusted_weights:
            adjusted_weights[key] /= total
        
        logger.debug(f"Poids temporels ajustés pour l'utilisateur {user_id}: {adjusted_weights}")
        
        return adjusted_weights
    
    def get_user_temporal_params(self, user_id: int) -> Dict[str, float]:
        """
        Récupère les paramètres temporels pour un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Dictionnaire des paramètres temporels
        """
        try:
            if self.engine is None:
                logger.warning("Connexion à la base de données non disponible")
                return {}
                
            # Requête pour récupérer les paramètres
            query = """
            SELECT 
                recency_factor, change_rate, stability_score, last_updated
            FROM user_temporal_preferences
            WHERE user_id = :user_id
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(query), {"user_id": user_id})
                row = result.fetchone()
                
                if row:
                    return {
                        'recency_factor': float(row[0]),
                        'change_rate': float(row[1]),
                        'stability_score': float(row[2]),
                        'last_updated': row[3].isoformat() if row[3] else None
                    }
                else:
                    # Paramètres par défaut et les enregistrer
                    params = {
                        'recency_factor': self.recency_factor,
                        'change_rate': 0.5,  # Valeur par défaut médiane
                        'stability_score': 0.5  # Valeur par défaut médiane
                    }
                    
                    self.set_user_temporal_params(user_id, params)
                    
                    return params
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des paramètres temporels: {e}")
            return {}
    
    def set_user_temporal_params(self, user_id: int, params: Dict[str, float]) -> bool:
        """
        Définit les paramètres temporels pour un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            params: Paramètres temporels à définir
            
        Returns:
            True si la mise à jour a réussi, False sinon
        """
        try:
            if self.engine is None:
                logger.warning("Connexion à la base de données non disponible")
                return False
                
            # Vérifier si des paramètres existent déjà
            check_query = """
            SELECT user_id FROM user_temporal_preferences
            WHERE user_id = :user_id
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(check_query), {"user_id": user_id})
                existing = result.fetchone()
                
                if existing:
                    # Mettre à jour les paramètres existants
                    update_query = """
                    UPDATE user_temporal_preferences
                    SET 
                        recency_factor = :recency_factor,
                        change_rate = :change_rate,
                        stability_score = :stability_score,
                        last_updated = CURRENT_TIMESTAMP
                    WHERE user_id = :user_id
                    """
                    
                    conn.execute(text(update_query), {
                        "user_id": user_id,
                        "recency_factor": params.get('recency_factor', self.recency_factor),
                        "change_rate": params.get('change_rate', 0.5),
                        "stability_score": params.get('stability_score', 0.5)
                    })
                else:
                    # Créer de nouveaux paramètres
                    insert_query = """
                    INSERT INTO user_temporal_preferences (
                        user_id, recency_factor, change_rate, stability_score
                    ) VALUES (
                        :user_id, :recency_factor, :change_rate, :stability_score
                    )
                    """
                    
                    conn.execute(text(insert_query), {
                        "user_id": user_id,
                        "recency_factor": params.get('recency_factor', self.recency_factor),
                        "change_rate": params.get('change_rate', 0.5),
                        "stability_score": params.get('stability_score', 0.5)
                    })
                
                conn.commit()
            
            logger.debug(f"Paramètres temporels mis à jour pour l'utilisateur {user_id}: {params}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des paramètres temporels: {e}")
            return False
    
    def update_user_stability(self, user_id: int) -> Dict[str, float]:
        """
        Met à jour et retourne le score de stabilité des préférences d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Paramètres temporels mis à jour
        """
        try:
            # Calculer la stabilité des préférences
            stability = self._calculate_preference_stability(user_id)
            
            if stability is None:
                logger.warning(f"Pas assez de données pour calculer la stabilité pour l'utilisateur {user_id}")
                return self.get_user_temporal_params(user_id)
            
            # Récupérer les paramètres actuels
            current_params = self.get_user_temporal_params(user_id)
            
            # Mettre à jour les paramètres
            updated_params = current_params.copy()
            updated_params['stability_score'] = stability
            
            # Ajuster le facteur de récence en fonction de la stabilité
            # Plus les préférences sont instables, plus on donne d'importance aux actions récentes
            updated_params['recency_factor'] = min(0.9, max(0.1, 1.0 - stability))
            
            # Sauvegarder les paramètres mis à jour
            self.set_user_temporal_params(user_id, updated_params)
            
            logger.info(f"Stabilité mise à jour pour l'utilisateur {user_id}: {stability:.2f}")
            
            return updated_params
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de la stabilité: {e}")
            return self.get_user_temporal_params(user_id)
    
    def _calculate_recent_weights(self, user_id: int) -> Dict[str, float]:
        """
        Calcule les poids basés sur l'activité récente de l'utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Poids basés sur l'activité récente
        """
        try:
            if self.engine is None:
                logger.warning("Connexion à la base de données non disponible")
                return {}
                
            # Récupérer l'historique des poids
            query = """
            SELECT 
                skills_weight, contract_weight, location_weight, 
                date_weight, salary_weight, experience_weight,
                soft_skills_weight, culture_weight,
                created_at
            FROM user_matching_weights_history
            WHERE user_id = :user_id
            ORDER BY created_at DESC
            LIMIT 20
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(query), {"user_id": user_id})
                
                rows = result.fetchall()
                if not rows:
                    return {}
                
                # Initialiser les poids avec des zéros
                weighted_sum = {
                    'skills': 0.0,
                    'contract': 0.0,
                    'location': 0.0,
                    'date': 0.0,
                    'salary': 0.0,
                    'experience': 0.0,
                    'soft_skills': 0.0,
                    'culture': 0.0
                }
                total_weight = 0.0
                
                # Date de référence (maintenant)
                now = datetime.now()
                
                # Calculer la moyenne pondérée avec décroissance exponentielle
                for row in rows:
                    # Calculer le poids temporel
                    timestamp = row[8]
                    age_days = (now - timestamp).total_seconds() / (24 * 3600)
                    time_weight = math.exp(-age_days * math.log(2) / self.half_life_days)
                    
                    # Appliquer le poids aux valeurs
                    weighted_sum['skills'] += float(row[0]) * time_weight
                    weighted_sum['contract'] += float(row[1]) * time_weight
                    weighted_sum['location'] += float(row[2]) * time_weight
                    weighted_sum['date'] += float(row[3]) * time_weight
                    weighted_sum['salary'] += float(row[4]) * time_weight
                    weighted_sum['experience'] += float(row[5]) * time_weight
                    weighted_sum['soft_skills'] += float(row[6]) * time_weight
                    weighted_sum['culture'] += float(row[7]) * time_weight
                    
                    total_weight += time_weight
                
                # Normaliser les poids
                if total_weight > 0:
                    for key in weighted_sum:
                        weighted_sum[key] /= total_weight
                
                return weighted_sum
        except Exception as e:
            logger.error(f"Erreur lors du calcul des poids récents: {e}")
            return {}
    
    def _calculate_preference_stability(self, user_id: int) -> Optional[float]:
        """
        Calcule la stabilité des préférences d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Score de stabilité (0-1) ou None si pas assez de données
        """
        try:
            if self.engine is None:
                logger.warning("Connexion à la base de données non disponible")
                return None
                
            # Récupérer l'historique des poids
            query = """
            SELECT 
                skills_weight, contract_weight, location_weight, 
                date_weight, salary_weight, experience_weight,
                soft_skills_weight, culture_weight,
                created_at
            FROM user_matching_weights_history
            WHERE user_id = :user_id
            ORDER BY created_at DESC
            LIMIT 10
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(query), {"user_id": user_id})
                
                rows = list(result.fetchall())
                if len(rows) < 3:
                    # Pas assez de données pour calculer la stabilité
                    return None
                
                # Créer une matrice de poids
                weights_matrix = np.array([
                    [
                        float(row[0]), float(row[1]), float(row[2]), 
                        float(row[3]), float(row[4]), float(row[5]),
                        float(row[6]), float(row[7])
                    ] 
                    for row in rows
                ])
                
                # Calculer la variance pour chaque critère
                variances = np.var(weights_matrix, axis=0)
                
                # Calculer le score de stabilité (inversement proportionnel à la variance)
                avg_variance = np.mean(variances)
                stability_score = 1.0 / (1.0 + 10.0 * avg_variance)
                
                return min(1.0, max(0.0, stability_score))
        except Exception as e:
            logger.error(f"Erreur lors du calcul de la stabilité des préférences: {e}")
            return None
    
    def analyze_temporal_trends(self, user_id: int) -> Dict[str, Any]:
        """
        Analyse les tendances temporelles des préférences d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Dictionnaire avec les tendances identifiées
        """
        try:
            if self.engine is None:
                logger.warning("Connexion à la base de données non disponible")
                return {
                    'trends': [],
                    'change_detected': False,
                    'stability': None
                }
                
            # Récupérer l'historique des poids
            query = """
            SELECT 
                skills_weight, contract_weight, location_weight, 
                date_weight, salary_weight, experience_weight,
                soft_skills_weight, culture_weight,
                created_at
            FROM user_matching_weights_history
            WHERE user_id = :user_id
            ORDER BY created_at ASC
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(query), {"user_id": user_id})
                
                rows = list(result.fetchall())
                if len(rows) < 5:
                    # Pas assez de données pour analyser les tendances
                    return {
                        'trends': [],
                        'change_detected': False,
                        'stability': None
                    }
                
                # Créer un DataFrame pour l'analyse
                df = pd.DataFrame([
                    {
                        'skills': float(row[0]),
                        'contract': float(row[1]),
                        'location': float(row[2]),
                        'date': float(row[3]),
                        'salary': float(row[4]),
                        'experience': float(row[5]),
                        'soft_skills': float(row[6]),
                        'culture': float(row[7]),
                        'timestamp': row[8]
                    }
                    for row in rows
                ])
                
                # Définir des points dans le temps pour l'analyse
                if len(df) >= 10:
                    # Diviser en 3 périodes
                    early = df.iloc[:len(df)//3]
                    middle = df.iloc[len(df)//3:2*len(df)//3]
                    recent = df.iloc[2*len(df)//3:]
                    
                    # Calculer les moyennes pour chaque période
                    early_avg = early.drop('timestamp', axis=1).mean()
                    middle_avg = middle.drop('timestamp', axis=1).mean()
                    recent_avg = recent.drop('timestamp', axis=1).mean()
                    
                    # Identifier les tendances
                    trends = []
                    change_detected = False
                    
                    # Seuil de changement significatif
                    threshold = 0.05
                    
                    for criterion in early_avg.index:
                        early_val = early_avg[criterion]
                        middle_val = middle_avg[criterion]
                        recent_val = recent_avg[criterion]
                        
                        # Calculer les changements
                        early_to_middle = middle_val - early_val
                        middle_to_recent = recent_val - middle_val
                        overall_change = recent_val - early_val
                        
                        # Évaluer la tendance
                        if abs(overall_change) > threshold:
                            change_detected = True
                            
                            # Vérifier si la tendance est continue
                            if (early_to_middle > 0 and middle_to_recent > 0) or \
                               (early_to_middle < 0 and middle_to_recent < 0):
                                trend_type = "consistent"
                            else:
                                trend_type = "variable"
                            
                            trends.append({
                                'criterion': criterion,
                                'trend': 'increasing' if overall_change > 0 else 'decreasing',
                                'type': trend_type,
                                'magnitude': abs(overall_change),
                                'early_value': float(early_val),
                                'recent_value': float(recent_val)
                            })
                    
                    # Trier les tendances par magnitude
                    trends.sort(key=lambda x: x['magnitude'], reverse=True)
                    
                    # Calculer la stabilité globale
                    stability = self._calculate_preference_stability(user_id)
                    
                    return {
                        'trends': trends,
                        'change_detected': change_detected,
                        'stability': stability
                    }
                else:
                    return {
                        'trends': [],
                        'change_detected': False,
                        'stability': None
                    }
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse des tendances temporelles: {e}")
            return {
                'trends': [],
                'change_detected': False,
                'stability': None
            }
