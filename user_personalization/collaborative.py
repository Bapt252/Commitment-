"""
Module de filtrage collaboratif pour la personnalisation des matchs.
"""

import logging
from typing import List, Dict, Any
import numpy as np

logger = logging.getLogger(__name__)

class CollaborativeFilter:
    """
    Implémentation d'un système de filtrage collaboratif
    pour la personnalisation des recommandations.
    """
    
    def __init__(self, db_connection):
        """
        Initialise le filtrage collaboratif avec une connexion à la base de données.
        
        Args:
            db_connection: Connexion à la base de données
        """
        self.db = db_connection
        logger.info("CollaborativeFilter initialized")
    
    def get_candidate_scores(self, user_id: int, candidates: List[Dict[str, Any]]) -> Dict[int, float]:
        """
        Calcule les scores de similarité collaborative pour une liste de candidats.
        
        Args:
            user_id: ID de l'utilisateur
            candidates: Liste des candidats potentiels
            
        Returns:
            Dictionnaire des scores par candidat {candidate_id: score}
        """
        try:
            # Récupérer les utilisateurs similaires
            similar_users = self._get_similar_users(user_id)
            
            if not similar_users:
                logger.warning(f"No similar users found for user {user_id}")
                return {candidate["id"]: 0.0 for candidate in candidates}
            
            # Récupérer les interactions des utilisateurs similaires avec les candidats
            interactions = self._get_user_interactions(similar_users.keys(), [c["id"] for c in candidates])
            
            # Calculer les scores pour chaque candidat
            scores = {}
            for candidate in candidates:
                candidate_id = candidate["id"]
                score = self._calculate_collaborative_score(candidate_id, similar_users, interactions)
                scores[candidate_id] = score
            
            # Normaliser les scores entre 0 et 1
            if scores and max(scores.values()) > 0:
                max_score = max(scores.values())
                scores = {cid: score/max_score for cid, score in scores.items()}
            
            return scores
            
        except Exception as e:
            logger.error(f"Error calculating collaborative scores: {e}")
            return {candidate["id"]: 0.0 for candidate in candidates}
    
    def update_from_feedback(self, user_id: int, candidate_id: int, 
                           feedback_type: str, feedback_value: Any) -> bool:
        """
        Met à jour les données de filtrage collaboratif basées sur le feedback.
        
        Args:
            user_id: ID de l'utilisateur
            candidate_id: ID du candidat
            feedback_type: Type de feedback (like, dislike, match, etc.)
            feedback_value: Valeur du feedback
            
        Returns:
            True si la mise à jour a réussi, False sinon
        """
        try:
            # L'interaction est déjà enregistrée dans la table user_interactions
            # par le module weights.py, pas besoin de le refaire ici
            
            # Mettre à jour la table de similarité utilisateur
            self._update_user_similarity(user_id)
            
            logger.info(f"Updated collaborative data for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating collaborative data: {e}")
            return False
    
    def _get_similar_users(self, user_id: int) -> Dict[int, float]:
        """
        Récupère les utilisateurs similaires et leurs scores de similarité.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Dictionnaire {user_id: similarity_score}
        """
        cursor = self.db.cursor()
        
        # Récupérer les utilisateurs similaires précalculés
        cursor.execute(
            """
            SELECT similar_user_id, similarity_score
            FROM user_similarity
            WHERE user_id = %s
            ORDER BY similarity_score DESC
            LIMIT 50
            """,
            (user_id,)
        )
        
        results = cursor.fetchall()
        
        # Construire le dictionnaire des scores
        similar_users = {}
        for row in results:
            similar_users[row['similar_user_id']] = row['similarity_score']
        
        return similar_users
    
    def _get_user_interactions(self, user_ids: List[int], candidate_ids: List[int]) -> Dict[tuple, float]:
        """
        Récupère les interactions des utilisateurs avec les candidats.
        
        Args:
            user_ids: Liste des IDs utilisateurs
            candidate_ids: Liste des IDs candidats
            
        Returns:
            Dictionnaire {(user_id, candidate_id): score}
        """
        if not user_ids or not candidate_ids:
            return {}
        
        cursor = self.db.cursor()
        
        # Récupérer les interactions
        cursor.execute(
            """
            SELECT user_id, candidate_id, interaction_type, interaction_value
            FROM user_interactions
            WHERE user_id = ANY(%s) AND candidate_id = ANY(%s)
            """,
            (list(user_ids), candidate_ids)
        )
        
        results = cursor.fetchall()
        
        # Construire le dictionnaire des interactions
        interactions = {}
        for row in results:
            key = (row['user_id'], row['candidate_id'])
            
            # Convertir le type d'interaction en score numérique
            if row['interaction_value'] is not None:
                score = float(row['interaction_value'])
            else:
                # Valeurs par défaut selon le type d'interaction
                if row['interaction_type'] == 'like':
                    score = 1.0
                elif row['interaction_type'] == 'dislike':
                    score = -1.0
                elif row['interaction_type'] == 'match':
                    score = 2.0
                else:
                    score = 0.0
            
            interactions[key] = score
        
        return interactions
    
    def _calculate_collaborative_score(self, candidate_id: int, 
                                      similar_users: Dict[int, float],
                                      interactions: Dict[tuple, float]) -> float:
        """
        Calcule le score collaboratif pour un candidat.
        
        Args:
            candidate_id: ID du candidat
            similar_users: Dictionnaire des utilisateurs similaires {user_id: similarity_score}
            interactions: Dictionnaire des interactions {(user_id, candidate_id): score}
            
        Returns:
            Score collaboratif
        """
        numerator = 0.0
        denominator = 0.0
        
        for user_id, similarity in similar_users.items():
            interaction_key = (user_id, candidate_id)
            if interaction_key in interactions:
                interaction_score = interactions[interaction_key]
                numerator += similarity * interaction_score
                denominator += abs(similarity)
        
        if denominator > 0:
            return numerator / denominator
        
        return 0.0
    
    def _update_user_similarity(self, user_id: int) -> None:
        """
        Met à jour la table de similarité utilisateur pour un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
        """
        cursor = self.db.cursor()
        
        # Appeler une fonction SQL qui recalculerait les similarités
        # Cette partie dépendrait de l'implémentation spécifique de votre
        # algorithme de similarité (cosinus, Pearson, etc.)
        
        # Exemple simplifié (à implémenter selon vos besoins)
        cursor.execute(
            """
            -- Cette requête est un placeholder et devrait être remplacée
            -- par votre implémentation spécifique
            WITH user_vectors AS (
                SELECT 
                    user_id,
                    jsonb_object_agg(candidate_id, interaction_value) AS vector
                FROM user_interactions
                WHERE interaction_type IN ('like', 'match')
                GROUP BY user_id
            )
            -- Ici, vous calculeriez les similarités entre les vecteurs
            -- et mettriez à jour la table user_similarity
            """
        )
        
        self.db.commit()
