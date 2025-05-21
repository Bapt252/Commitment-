"""
Module de gestion des poids personnalisés pour le matching.
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class UserWeights:
    """
    Classe pour stocker les poids personnalisés d'un utilisateur.
    """
    attribute_weights: Dict[str, float]
    category_modifiers: Dict[str, float]


class WeightManager:
    """
    Gestionnaire des poids personnalisés.
    """
    
    def __init__(self, db_connection):
        """
        Initialise le gestionnaire de poids avec une connexion à la base de données.
        
        Args:
            db_connection: Connexion à la base de données
        """
        self.db = db_connection
        logger.info("WeightManager initialized")
    
    def get_user_weights(self, user_id: int) -> Optional[UserWeights]:
        """
        Récupère les poids personnalisés d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            UserWeights ou None si l'utilisateur n'existe pas
        """
        try:
            cursor = self.db.cursor()
            
            # Utiliser la vue pour obtenir tous les poids personnalisés
            cursor.execute(
                """
                SELECT attribute_weights, category_modifiers
                FROM user_personalization_profile
                WHERE user_id = %s
                """,
                (user_id,)
            )
            
            result = cursor.fetchone()
            
            if result:
                return UserWeights(
                    attribute_weights=result['attribute_weights'],
                    category_modifiers=result['category_modifiers']
                )
            else:
                logger.warning(f"No weights found for user {user_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting user weights: {e}")
            raise
    
    def update_from_feedback(self, user_id: int, candidate_id: int, 
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
            cursor = self.db.cursor()
            
            # Appeler la fonction de mise à jour des poids
            cursor.execute(
                """
                SELECT update_weights_from_feedback(%s, %s, %s, %s)
                """,
                (user_id, candidate_id, feedback_type, feedback_value)
            )
            
            self.db.commit()
            
            logger.info(f"Updated weights for user {user_id} based on feedback")
            return True
            
        except Exception as e:
            logger.error(f"Error updating weights from feedback: {e}")
            self.db.rollback()
            return False
    
    def set_attribute_weight(self, user_id: int, attribute: str, weight: float) -> bool:
        """
        Définit le poids d'un attribut pour un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            attribute: Nom de l'attribut
            weight: Nouveau poids
            
        Returns:
            True si la mise à jour a réussi, False sinon
        """
        try:
            cursor = self.db.cursor()
            
            # Obtenir l'ID de l'attribut
            cursor.execute(
                """
                SELECT id FROM personalization_attributes
                WHERE attribute_name = %s
                """,
                (attribute,)
            )
            
            attr_result = cursor.fetchone()
            if not attr_result:
                logger.warning(f"Attribute {attribute} not found")
                return False
            
            attribute_id = attr_result['id']
            
            # Mettre à jour ou insérer le poids
            cursor.execute(
                """
                INSERT INTO user_attribute_weights (user_id, attribute_id, weight)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, attribute_id) 
                DO UPDATE SET weight = %s, updated_at = CURRENT_TIMESTAMP
                """,
                (user_id, attribute_id, weight, weight)
            )
            
            self.db.commit()
            
            logger.info(f"Set attribute weight {attribute}={weight} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting attribute weight: {e}")
            self.db.rollback()
            return False
    
    def set_category_modifier(self, user_id: int, category: str, modifier: float) -> bool:
        """
        Définit le modificateur d'une catégorie pour un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            category: Nom de la catégorie
            modifier: Nouveau modificateur
            
        Returns:
            True si la mise à jour a réussi, False sinon
        """
        try:
            cursor = self.db.cursor()
            
            # Obtenir l'ID de la catégorie
            cursor.execute(
                """
                SELECT id FROM personalization_categories
                WHERE category_name = %s
                """,
                (category,)
            )
            
            cat_result = cursor.fetchone()
            if not cat_result:
                logger.warning(f"Category {category} not found")
                return False
            
            category_id = cat_result['id']
            
            # Mettre à jour ou insérer le modificateur
            cursor.execute(
                """
                INSERT INTO user_category_modifiers (user_id, category_id, modifier)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, category_id) 
                DO UPDATE SET modifier = %s, updated_at = CURRENT_TIMESTAMP
                """,
                (user_id, category_id, modifier, modifier)
            )
            
            self.db.commit()
            
            logger.info(f"Set category modifier {category}={modifier} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting category modifier: {e}")
            self.db.rollback()
            return False
