"""
Module de tests A/B pour optimiser les stratégies de personnalisation.
"""

import logging
from typing import Dict, Any, Optional
import random

logger = logging.getLogger(__name__)

class ABTestManager:
    """
    Gestionnaire des tests A/B pour la personnalisation.
    """
    
    def __init__(self, db_connection):
        """
        Initialise le gestionnaire de tests A/B avec une connexion à la base de données.
        
        Args:
            db_connection: Connexion à la base de données
        """
        self.db = db_connection
        logger.info("ABTestManager initialized")
    
    def get_user_variant(self, user_id: int) -> Optional[str]:
        """
        Récupère la variante de test A/B assignée à l'utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Nom de la variante ou None si l'utilisateur n'est pas dans un test
        """
        try:
            cursor = self.db.cursor()
            
            # Vérifier si l'utilisateur est déjà assigné à un test A/B
            cursor.execute(
                """
                SELECT v.variant_name
                FROM user_ab_test_assignments ua
                JOIN ab_test_variants v ON ua.variant_id = v.id
                JOIN ab_tests t ON v.test_id = t.id
                WHERE ua.user_id = %s
                AND t.test_name = 'weight_balance'
                AND t.active = TRUE
                """,
                (user_id,)
            )
            
            result = cursor.fetchone()
            
            if result:
                return result['variant_name']
            
            # Si l'utilisateur n'est pas encore assigné, lui assigner une variante
            return self._assign_user_to_variant(user_id)
            
        except Exception as e:
            logger.error(f"Error getting user variant: {e}")
            return None
    
    def record_metric(self, user_id: int, metric_name: str, metric_value: Any) -> bool:
        """
        Enregistre une métrique pour un utilisateur dans un test A/B.
        
        Args:
            user_id: ID de l'utilisateur
            metric_name: Nom de la métrique
            metric_value: Valeur de la métrique
            
        Returns:
            True si l'enregistrement a réussi, False sinon
        """
        try:
            # Vérifier si l'utilisateur est dans un test A/B
            variant = self.get_user_variant(user_id)
            
            if not variant:
                # L'utilisateur n'est pas dans un test A/B, pas besoin d'enregistrer
                return True
            
            cursor = self.db.cursor()
            
            # Récupérer l'ID de la variante
            cursor.execute(
                """
                SELECT v.id
                FROM ab_test_variants v
                JOIN ab_tests t ON v.test_id = t.id
                WHERE v.variant_name = %s
                AND t.test_name = 'weight_balance'
                AND t.active = TRUE
                """,
                (variant,)
            )
            
            variant_result = cursor.fetchone()
            
            if not variant_result:
                logger.warning(f"Variant {variant} not found or test not active")
                return False
            
            variant_id = variant_result['id']
            
            # Convertir la valeur en nombre si possible
            numeric_value = self._convert_to_numeric(metric_value)
            
            # Enregistrer la métrique
            cursor.execute(
                """
                INSERT INTO ab_test_metrics
                    (user_id, variant_id, metric_name, metric_value)
                VALUES
                    (%s, %s, %s, %s)
                """,
                (user_id, variant_id, metric_name, numeric_value)
            )
            
            self.db.commit()
            
            logger.info(f"Recorded metric {metric_name}={numeric_value} for user {user_id} in variant {variant}")
            return True
            
        except Exception as e:
            logger.error(f"Error recording metric: {e}")
            self.db.rollback()
            return False
    
    def _assign_user_to_variant(self, user_id: int) -> Optional[str]:
        """
        Assigne un utilisateur à une variante de test A/B.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Nom de la variante assignée ou None en cas d'erreur
        """
        cursor = self.db.cursor()
        
        # Récupérer les variantes disponibles avec leurs poids
        cursor.execute(
            """
            SELECT v.id, v.variant_name, v.distribution_weight
            FROM ab_test_variants v
            JOIN ab_tests t ON v.test_id = t.id
            WHERE t.test_name = 'weight_balance'
            AND t.active = TRUE
            """
        )
        
        variants = cursor.fetchall()
        
        if not variants:
            logger.warning("No active variants found for weight_balance test")
            return None
        
        # Sélectionner une variante selon les poids de distribution
        variant = self._select_weighted_variant(variants)
        
        if not variant:
            return None
        
        # Assigner l'utilisateur à la variante
        try:
            cursor.execute(
                """
                INSERT INTO user_ab_test_assignments
                    (user_id, variant_id)
                VALUES
                    (%s, %s)
                """,
                (user_id, variant['id'])
            )
            
            self.db.commit()
            
            logger.info(f"Assigned user {user_id} to variant {variant['variant_name']}")
            return variant['variant_name']
            
        except Exception as e:
            logger.error(f"Error assigning user to variant: {e}")
            self.db.rollback()
            return None
    
    def _select_weighted_variant(self, variants: list) -> Optional[Dict[str, Any]]:
        """
        Sélectionne une variante selon les poids de distribution.
        
        Args:
            variants: Liste des variantes avec leurs poids
            
        Returns:
            Variante sélectionnée ou None si la liste est vide
        """
        if not variants:
            return None
        
        # Calculer le poids total
        total_weight = sum(v['distribution_weight'] for v in variants)
        
        if total_weight <= 0:
            # Si tous les poids sont nuls, sélectionner aléatoirement
            return random.choice(variants)
        
        # Sélectionner selon les poids
        r = random.uniform(0, total_weight)
        cumulative_weight = 0
        
        for variant in variants:
            cumulative_weight += variant['distribution_weight']
            if r <= cumulative_weight:
                return variant
        
        # Fallback au cas où
        return variants[-1]
    
    def _convert_to_numeric(self, value: Any) -> float:
        """
        Convertit une valeur en nombre pour l'enregistrement des métriques.
        
        Args:
            value: Valeur à convertir
            
        Returns:
            Valeur numérique
        """
        if isinstance(value, (int, float)):
            return float(value)
        elif isinstance(value, bool):
            return 1.0 if value else 0.0
        else:
            try:
                return float(value)
            except (ValueError, TypeError):
                return 0.0
