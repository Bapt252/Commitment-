"""
Module de gestion des utilisateurs nouveaux (cold start).
"""

import logging
from typing import List, Dict, Any
import random

logger = logging.getLogger(__name__)

class ColdStartStrategy:
    """
    Stratégies pour recommander des matchs aux nouveaux utilisateurs.
    """
    
    def __init__(self, db_connection):
        """
        Initialise la stratégie cold start avec une connexion à la base de données.
        
        Args:
            db_connection: Connexion à la base de données
        """
        self.db = db_connection
        logger.info("ColdStartStrategy initialized")
    
    def is_cold_start_user(self, user_id: int) -> bool:
        """
        Détermine si un utilisateur est un nouvel utilisateur (cold start).
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            True si l'utilisateur est un nouvel utilisateur, False sinon
        """
        try:
            cursor = self.db.cursor()
            
            # Vérifier le nombre d'interactions de l'utilisateur
            cursor.execute(
                """
                SELECT COUNT(*) as interaction_count
                FROM user_interactions
                WHERE user_id = %s
                """,
                (user_id,)
            )
            
            result = cursor.fetchone()
            
            # Si moins de 5 interactions, considérer comme cold start
            return result['interaction_count'] < 5
            
        except Exception as e:
            logger.error(f"Error checking if user is cold start: {e}")
            # Par défaut, traiter comme un utilisateur normal
            return False
    
    def get_recommendations(self, user_id: int, candidates: List[Dict[str, Any]], 
                           limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtient des recommandations pour un nouvel utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            candidates: Liste des candidats potentiels
            limit: Nombre maximum de recommandations
            
        Returns:
            Liste des candidats recommandés
        """
        try:
            # Récupérer les caractéristiques de l'utilisateur
            user_profile = self._get_user_profile(user_id)
            
            # Vérifier quelle stratégie appliquer selon le test A/B
            strategy = self._get_ab_test_strategy(user_id)
            
            # Appliquer la stratégie appropriée
            if strategy == 'demographic':
                recommendations = self._apply_demographic_strategy(user_profile, candidates, limit)
            else:
                # Stratégie par défaut (populaire)
                recommendations = self._apply_popularity_strategy(candidates, limit)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting cold start recommendations: {e}")
            # En cas d'erreur, retourner une liste aléatoire
            random.shuffle(candidates)
            return candidates[:limit]
    
    def _get_user_profile(self, user_id: int) -> Dict[str, Any]:
        """
        Récupère le profil de l'utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Dictionnaire des caractéristiques de l'utilisateur
        """
        cursor = self.db.cursor()
        
        # Récupérer les informations de base de l'utilisateur
        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE id = %s
            """,
            (user_id,)
        )
        
        user = cursor.fetchone()
        
        if not user:
            logger.warning(f"User {user_id} not found")
            return {}
        
        # Récupérer les préférences de l'utilisateur
        cursor.execute(
            """
            SELECT *
            FROM user_preferences
            WHERE user_id = %s
            """,
            (user_id,)
        )
        
        preferences = cursor.fetchone() or {}
        
        # Combiner les informations
        profile = dict(user)
        profile.update(preferences)
        
        return profile
    
    def _get_ab_test_strategy(self, user_id: int) -> str:
        """
        Détermine quelle stratégie cold start appliquer selon le test A/B.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Nom de la stratégie à appliquer
        """
        cursor = self.db.cursor()
        
        # Vérifier si l'utilisateur est assigné à un test A/B
        cursor.execute(
            """
            SELECT v.variant_name
            FROM user_ab_test_assignments ua
            JOIN ab_test_variants v ON ua.variant_id = v.id
            JOIN ab_tests t ON v.test_id = t.id
            WHERE ua.user_id = %s
            AND t.test_name = 'cold_start_strategy'
            AND t.active = TRUE
            """,
            (user_id,)
        )
        
        result = cursor.fetchone()
        
        if result:
            return result['variant_name']
        else:
            # Assigner aléatoirement à une variante
            strategies = ['control', 'demographic']
            return random.choice(strategies)
    
    def _apply_demographic_strategy(self, user_profile: Dict[str, Any], 
                                  candidates: List[Dict[str, Any]], 
                                  limit: int) -> List[Dict[str, Any]]:
        """
        Applique une stratégie basée sur les caractéristiques démographiques.
        
        Args:
            user_profile: Profil de l'utilisateur
            candidates: Liste des candidats potentiels
            limit: Nombre maximum de recommandations
            
        Returns:
            Liste des candidats recommandés
        """
        scored_candidates = []
        
        for candidate in candidates:
            score = 0.0
            
            # Score basé sur l'âge
            if 'age' in user_profile and 'age' in candidate:
                age_diff = abs(user_profile['age'] - candidate['age'])
                # Plus la différence d'âge est petite, plus le score est élevé
                score += max(0, 1.0 - (age_diff / 20.0))
            
            # Score basé sur la localisation
            if 'location' in user_profile and 'location' in candidate:
                if user_profile['location'] == candidate['location']:
                    score += 1.0
            
            # Score basé sur les intérêts
            if 'interests' in user_profile and 'interests' in candidate:
                user_interests = set(user_profile['interests'].split(','))
                candidate_interests = set(candidate['interests'].split(','))
                common_interests = user_interests.intersection(candidate_interests)
                score += len(common_interests) * 0.5
            
            scored_candidates.append((candidate, score))
        
        # Trier par score décroissant
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Retourner les candidats triés avec leur score
        results = []
        for candidate, score in scored_candidates[:limit]:
            result = candidate.copy()
            result['personalized_score'] = score
            results.append(result)
        
        return results
    
    def _apply_popularity_strategy(self, candidates: List[Dict[str, Any]], 
                                 limit: int) -> List[Dict[str, Any]]:
        """
        Applique une stratégie basée sur la popularité.
        
        Args:
            candidates: Liste des candidats potentiels
            limit: Nombre maximum de recommandations
            
        Returns:
            Liste des candidats recommandés
        """
        cursor = self.db.cursor()
        
        # Récupérer les candidats populaires
        cursor.execute(
            """
            SELECT candidate_id, COUNT(*) as interaction_count
            FROM user_interactions
            WHERE interaction_type IN ('like', 'match')
            AND candidate_id = ANY(%s)
            GROUP BY candidate_id
            ORDER BY interaction_count DESC
            LIMIT %s
            """,
            ([c["id"] for c in candidates], limit)
        )
        
        popular_ids = [row['candidate_id'] for row in cursor.fetchall()]
        
        # Si pas assez de candidats populaires, compléter avec des candidats aléatoires
        if len(popular_ids) < limit:
            remaining_candidates = [c for c in candidates if c["id"] not in popular_ids]
            random.shuffle(remaining_candidates)
            additional_ids = [c["id"] for c in remaining_candidates[:limit - len(popular_ids)]]
            popular_ids.extend(additional_ids)
        
        # Organiser les candidats dans l'ordre des IDs populaires
        id_to_candidate = {c["id"]: c for c in candidates}
        results = []
        
        for idx, cid in enumerate(popular_ids):
            if cid in id_to_candidate:
                candidate = id_to_candidate[cid].copy()
                # Score basé sur le rang de popularité
                candidate['personalized_score'] = 1.0 - (idx / limit) if limit > 0 else 0
                results.append(candidate)
        
        return results
