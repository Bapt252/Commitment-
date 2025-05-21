"""
Module principal de personnalisation qui combine toutes les stratégies
pour fournir des matchs personnalisés aux utilisateurs.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple

from .weights import UserWeights, WeightManager
from .collaborative import CollaborativeFilter
from .cold_start import ColdStartStrategy
from .temporal import TemporalAdjustment
from .ab_testing import ABTestManager

logger = logging.getLogger(__name__)

class PersonalizedMatcher:
    """
    Classe principale qui combine toutes les stratégies de personnalisation
    pour fournir un matching personnalisé aux utilisateurs.
    """
    
    def __init__(self, db_connection, config=None):
        """
        Initialise le matcher personnalisé avec une connexion à la base de données
        et une configuration optionnelle.
        
        Args:
            db_connection: Connexion à la base de données
            config: Configuration optionnelle pour le matcher
        """
        self.db = db_connection
        self.config = config or {}
        
        # Initialisation des composants
        self.weight_manager = WeightManager(db_connection)
        self.collaborative_filter = CollaborativeFilter(db_connection)
        self.cold_start = ColdStartStrategy(db_connection)
        self.temporal = TemporalAdjustment(db_connection)
        self.ab_test_manager = ABTestManager(db_connection)
        
        logger.info("PersonalizedMatcher initialized")
    
    def get_personalized_matches(self, user_id: int, 
                                 base_candidates: List[Dict[str, Any]],
                                 limit: int = 10,
                                 context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Obtient une liste de matchs personnalisés pour un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            base_candidates: Liste initiale de candidats potentiels (avec leurs attributs)
            limit: Nombre maximum de matchs à retourner
            context: Contexte supplémentaire pour le matching (heure, localisation, etc.)
            
        Returns:
            Liste des candidats triés par pertinence personnalisée
        """
        context = context or {}
        
        # Vérifier si l'utilisateur participe à un test A/B
        ab_variant = self.ab_test_manager.get_user_variant(user_id)
        
        # Obtenir les poids personnalisés de l'utilisateur
        try:
            user_weights = self.weight_manager.get_user_weights(user_id)
        except Exception as e:
            logger.warning(f"Failed to get user weights for user {user_id}: {e}")
            user_weights = None
        
        # Appliquer la stratégie cold start pour les nouveaux utilisateurs
        if user_weights is None or self.cold_start.is_cold_start_user(user_id):
            logger.info(f"Applying cold start strategy for user {user_id}")
            candidates = self.cold_start.get_recommendations(user_id, base_candidates, limit)
        else:
            # Appliquer le filtrage collaboratif
            collab_scores = self.collaborative_filter.get_candidate_scores(user_id, base_candidates)
            
            # Appliquer les poids personnalisés
            weighted_scores = self._apply_user_weights(user_id, base_candidates, user_weights)
            
            # Appliquer les ajustements temporels
            temporal_scores = self.temporal.adjust_scores(user_id, 
                                                         {c["id"]: weighted_scores.get(c["id"], 0) 
                                                          for c in base_candidates},
                                                         context)
            
            # Combiner les scores et trier les candidats
            candidates = self._combine_scores(base_candidates, collab_scores, weighted_scores, 
                                            temporal_scores, ab_variant)
            
            # Limiter le nombre de résultats
            candidates = candidates[:limit]
        
        return candidates
    
    def update_feedback(self, user_id: int, candidate_id: int, 
                       feedback_type: str, feedback_value: Any) -> bool:
        """
        Met à jour les poids basés sur le feedback de l'utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            candidate_id: ID du candidat
            feedback_type: Type de feedback (like, dislike, match, etc.)
            feedback_value: Valeur du feedback
            
        Returns:
            True si la mise à jour a réussi, False sinon
        """
        try:
            # Mettre à jour les poids basés sur le feedback
            self.weight_manager.update_from_feedback(user_id, candidate_id, 
                                                   feedback_type, feedback_value)
            
            # Mettre à jour les données pour le filtrage collaboratif
            self.collaborative_filter.update_from_feedback(user_id, candidate_id, 
                                                         feedback_type, feedback_value)
            
            # Enregistrer l'interaction pour les ajustements temporels
            self.temporal.record_interaction(user_id, candidate_id, 
                                           feedback_type, feedback_value)
            
            # Enregistrer les métriques pour l'AB testing
            self.ab_test_manager.record_metric(user_id, feedback_type, feedback_value)
            
            return True
        except Exception as e:
            logger.error(f"Error updating feedback: {e}")
            return False
    
    def _apply_user_weights(self, user_id: int, candidates: List[Dict[str, Any]], 
                          user_weights: UserWeights) -> Dict[int, float]:
        """
        Applique les poids personnalisés de l'utilisateur aux candidats.
        
        Args:
            user_id: ID de l'utilisateur
            candidates: Liste des candidats
            user_weights: Poids personnalisés de l'utilisateur
            
        Returns:
            Dictionnaire des scores pondérés par candidat {candidate_id: score}
        """
        weighted_scores = {}
        
        for candidate in candidates:
            candidate_id = candidate["id"]
            score = 0.0
            
            # Calcul du score basé sur les attributs du candidat et les poids de l'utilisateur
            for attribute, weight in user_weights.attribute_weights.items():
                if attribute in candidate:
                    score += candidate[attribute] * weight
            
            # Appliquer les modifieurs de catégorie
            for category, modifier in user_weights.category_modifiers.items():
                if candidate.get("category") == category:
                    score *= modifier
            
            weighted_scores[candidate_id] = score
        
        return weighted_scores
    
    def _combine_scores(self, candidates: List[Dict[str, Any]],
                      collab_scores: Dict[int, float],
                      weighted_scores: Dict[int, float],
                      temporal_scores: Dict[int, float],
                      ab_variant: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Combine les différents scores pour obtenir un score final pour chaque candidat.
        
        Args:
            candidates: Liste des candidats
            collab_scores: Scores du filtrage collaboratif
            weighted_scores: Scores basés sur les poids personnalisés
            temporal_scores: Scores ajustés temporellement
            ab_variant: Variante A/B test pour l'utilisateur
            
        Returns:
            Liste des candidats triés par score final
        """
        # Facteurs de combinaison par défaut
        collab_factor = 0.4
        weight_factor = 0.4
        temporal_factor = 0.2
        
        # Ajuster les facteurs en fonction de la variante A/B
        if ab_variant == "collaborative_heavy":
            collab_factor = 0.6
            weight_factor = 0.3
            temporal_factor = 0.1
        elif ab_variant == "time_sensitive":
            collab_factor = 0.3
            weight_factor = 0.3
            temporal_factor = 0.4
        
        # Calculer les scores finaux
        final_scores = []
        for candidate in candidates:
            candidate_id = candidate["id"]
            
            collab_score = collab_scores.get(candidate_id, 0)
            weight_score = weighted_scores.get(candidate_id, 0)
            temp_score = temporal_scores.get(candidate_id, 0)
            
            # Score final combiné
            final_score = (collab_score * collab_factor +
                           weight_score * weight_factor +
                           temp_score * temporal_factor)
            
            # Créer une copie du candidat avec le score
            candidate_with_score = candidate.copy()
            candidate_with_score["personalized_score"] = final_score
            
            final_scores.append(candidate_with_score)
        
        # Trier par score décroissant
        final_scores.sort(key=lambda x: x["personalized_score"], reverse=True)
        
        return final_scores
