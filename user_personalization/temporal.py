"""
Module d'ajustements temporels pour la personnalisation des matchs.
"""

import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
import math

logger = logging.getLogger(__name__)

class TemporalAdjustment:
    """
    Ajustements temporels pour les recommandations personnalisées.
    """
    
    def __init__(self, db_connection):
        """
        Initialise les ajustements temporels avec une connexion à la base de données.
        
        Args:
            db_connection: Connexion à la base de données
        """
        self.db = db_connection
        logger.info("TemporalAdjustment initialized")
    
    def adjust_scores(self, user_id: int, candidate_scores: Dict[int, float], 
                     context: Dict[str, Any] = None) -> Dict[int, float]:
        """
        Ajuste les scores des candidats en fonction des patterns temporels.
        
        Args:
            user_id: ID de l'utilisateur
            candidate_scores: Scores initiaux des candidats {candidate_id: score}
            context: Contexte de la requête (heure, localisation, etc.)
            
        Returns:
            Scores ajustés {candidate_id: adjusted_score}
        """
        try:
            # Obtenir l'heure actuelle ou depuis le contexte
            current_time = context.get('timestamp') if context and 'timestamp' in context else datetime.now()
            
            # Obtenir les patterns temporels de l'utilisateur
            patterns = self._get_user_temporal_patterns(user_id)
            
            # Obtenir la dernière activité des candidats
            candidate_activity = self._get_candidate_activity([cid for cid in candidate_scores])
            
            # Ajuster les scores
            adjusted_scores = {}
            for candidate_id, score in candidate_scores.items():
                # Ajustement basé sur le moment de la journée
                time_factor = self._calculate_time_factor(patterns, current_time)
                
                # Ajustement basé sur la récence d'activité du candidat
                recency_factor = self._calculate_recency_factor(candidate_activity.get(candidate_id), current_time)
                
                # Score final ajusté
                adjusted_scores[candidate_id] = score * time_factor * recency_factor
            
            return adjusted_scores
            
        except Exception as e:
            logger.error(f"Error adjusting temporal scores: {e}")
            return candidate_scores
    
    def record_interaction(self, user_id: int, candidate_id: int, 
                         interaction_type: str, interaction_value: Any) -> bool:
        """
        Enregistre une interaction et met à jour les patterns temporels.
        
        Args:
            user_id: ID de l'utilisateur
            candidate_id: ID du candidat
            interaction_type: Type d'interaction
            interaction_value: Valeur de l'interaction
            
        Returns:
            True si l'enregistrement a réussi, False sinon
        """
        try:
            # L'interaction est déjà enregistrée dans la table user_interactions
            # par le module weights.py, pas besoin de le refaire ici
            
            # Mettre à jour les patterns temporels
            self._update_temporal_patterns(user_id)
            
            logger.info(f"Recorded interaction and updated temporal patterns for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error recording interaction for temporal adjustment: {e}")
            return False
    
    def _get_user_temporal_patterns(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Récupère les patterns temporels d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Liste des patterns temporels
        """
        cursor = self.db.cursor()
        
        cursor.execute(
            """
            SELECT day_of_week, hour_of_day, activity_level, pattern_type
            FROM user_temporal_patterns
            WHERE user_id = %s
            """,
            (user_id,)
        )
        
        return cursor.fetchall()
    
    def _get_candidate_activity(self, candidate_ids: List[int]) -> Dict[int, datetime]:
        """
        Récupère la dernière activité des candidats.
        
        Args:
            candidate_ids: Liste des IDs des candidats
            
        Returns:
            Dictionnaire {candidate_id: last_activity_timestamp}
        """
        if not candidate_ids:
            return {}
        
        cursor = self.db.cursor()
        
        cursor.execute(
            """
            SELECT id, last_activity
            FROM candidates
            WHERE id = ANY(%s)
            """,
            (candidate_ids,)
        )
        
        results = cursor.fetchall()
        
        # Construire le dictionnaire des dernières activités
        activity_dict = {}
        for row in results:
            activity_dict[row['id']] = row['last_activity']
        
        return activity_dict
    
    def _calculate_time_factor(self, patterns: List[Dict[str, Any]], current_time: datetime) -> float:
        """
        Calcule le facteur d'ajustement basé sur le moment de la journée.
        
        Args:
            patterns: Patterns temporels de l'utilisateur
            current_time: Heure actuelle
            
        Returns:
            Facteur d'ajustement (0.5 à 1.5)
        """
        # Jour de la semaine (0-6, lundi-dimanche)
        day_of_week = current_time.weekday()
        # Heure de la journée (0-23)
        hour_of_day = current_time.hour
        
        # Chercher un pattern correspondant
        for pattern in patterns:
            if pattern['day_of_week'] == day_of_week and pattern['hour_of_day'] == hour_of_day:
                # Utiliser le niveau d'activité comme facteur
                return 0.5 + pattern['activity_level']
        
        # Valeur par défaut si aucun pattern ne correspond
        return 1.0
    
    def _calculate_recency_factor(self, last_activity: datetime, current_time: datetime) -> float:
        """
        Calcule le facteur d'ajustement basé sur la récence d'activité.
        
        Args:
            last_activity: Dernière activité du candidat
            current_time: Heure actuelle
            
        Returns:
            Facteur d'ajustement (0.5 à 1.5)
        """
        if not last_activity:
            # Si pas d'activité connue, utiliser une valeur neutre
            return 1.0
        
        # Calculer la différence en heures
        diff_hours = (current_time - last_activity).total_seconds() / 3600
        
        # Fonction décroissante: plus récent = meilleur score
        # 1.5 pour très récent, 0.5 pour très ancien (> 1 semaine)
        if diff_hours < 24:
            # Moins de 24h: score élevé
            return 1.5 - (diff_hours / 48)
        elif diff_hours < 168:  # 7 jours
            # Entre 1 et 7 jours: score moyen
            return 1.0 - ((diff_hours - 24) / 288)
        else:
            # Plus de 7 jours: score faible
            return 0.5
    
    def _update_temporal_patterns(self, user_id: int) -> None:
        """
        Met à jour les patterns temporels d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
        """
        cursor = self.db.cursor()
        
        # Récupérer l'heure actuelle
        now = datetime.now()
        day_of_week = now.weekday()
        hour_of_day = now.hour
        
        # Mettre à jour ou insérer un pattern
        cursor.execute(
            """
            INSERT INTO user_temporal_patterns
                (user_id, day_of_week, hour_of_day, activity_level, pattern_type)
            VALUES
                (%s, %s, %s, %s, %s)
            ON CONFLICT (user_id, day_of_week, hour_of_day, pattern_type)
            DO UPDATE SET
                activity_level = (user_temporal_patterns.activity_level * 0.8 + 0.2),
                updated_at = CURRENT_TIMESTAMP
            """,
            (user_id, day_of_week, hour_of_day, 1.0, 'activity')
        )
        
        self.db.commit()
