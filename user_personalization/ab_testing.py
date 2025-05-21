"""
Module de tests A/B pour la personnalisation utilisateur
"""

import json
import logging
import random
import hashlib
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from user_personalization import (
    DEFAULT_DATABASE_URL, 
    AB_TEST_PARAMS,
    logger
)

class ABTestManager:
    """
    Gestionnaire des tests A/B pour la personnalisation.
    
    Cette classe permet de créer, gérer et analyser des tests A/B
    pour comparer différentes stratégies de personnalisation.
    """
    
    def __init__(self, db_url: Optional[str] = None):
        """
        Initialise le gestionnaire de tests A/B.
        
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
            
        # Paramètres des tests A/B
        self.assignment_method = AB_TEST_PARAMS.get('assignment_method', 'random')
        self.control_group_size = AB_TEST_PARAMS.get('control_group_size', 0.25)
        
        # Cache des tests actifs
        self._active_tests_cache = None
    
    def create_test(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crée un nouveau test A/B.
        
        Args:
            test_data: Données du test à créer
            
        Returns:
            Informations sur le test créé
        """
        try:
            if self.engine is None:
                logger.warning("Connexion à la base de données non disponible")
                return {
                    'success': False,
                    'error': 'database_connection_error'
                }
                
            # Valider les données obligatoires
            if 'name' not in test_data:
                return {
                    'success': False,
                    'error': 'missing_name'
                }
                
            if 'variants' not in test_data or not isinstance(test_data['variants'], list) or len(test_data['variants']) < 2:
                return {
                    'success': False,
                    'error': 'invalid_variants'
                }
                
            # Extraire les données du test
            test_name = test_data['name']
            description = test_data.get('description', '')
            variants = test_data['variants']
            duration_days = test_data.get('duration_days', 30)
            
            # Date de fin basée sur la durée
            end_date = datetime.now() + timedelta(days=duration_days)
            
            # Vérifier si un test avec le même nom existe déjà
            check_query = """
            SELECT id FROM personalization_ab_tests
            WHERE test_name = :test_name
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(check_query), {"test_name": test_name})
                existing = result.fetchone()
                
                if existing:
                    return {
                        'success': False,
                        'error': 'test_already_exists'
                    }
                
                # Créer le test
                query = """
                INSERT INTO personalization_ab_tests (
                    test_name, description, variants, 
                    start_date, end_date, status
                ) VALUES (
                    :test_name, :description, :variants, 
                    CURRENT_TIMESTAMP, :end_date, 'active'
                ) RETURNING id
                """
                
                result = conn.execute(text(query), {
                    "test_name": test_name,
                    "description": description,
                    "variants": json.dumps(variants),
                    "end_date": end_date
                })
                
                test_id = result.scalar()
                
                if not test_id:
                    conn.rollback()
                    return {
                        'success': False,
                        'error': 'insertion_failed'
                    }
                
                conn.commit()
            
            # Vider le cache des tests actifs
            self._active_tests_cache = None
            
            logger.info(f"Test A/B '{test_name}' créé avec {len(variants)} variantes")
            
            return {
                'success': True,
                'test_id': test_id,
                'test_name': test_name,
                'variants': variants,
                'end_date': end_date.isoformat()
            }
        except Exception as e:
            logger.error(f"Erreur lors de la création du test A/B: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_user_variant(self, user_id: int, test_name: str) -> Optional[str]:
        """
        Détermine la variante à laquelle un utilisateur est assigné.
        
        Si l'utilisateur n'est pas encore assigné, l'assigne à une variante.
        
        Args:
            user_id: ID de l'utilisateur
            test_name: Nom du test A/B
            
        Returns:
            Nom de la variante ou None si le test n'existe pas
        """
        try:
            if self.engine is None:
                logger.warning("Connexion à la base de données non disponible")
                return None
                
            # Vérifier si le test existe et est actif
            test_info = self._get_test_info(test_name)
            
            if not test_info or test_info.get('status') != 'active':
                logger.warning(f"Test '{test_name}' non trouvé ou inactif")
                return None
                
            test_id = test_info['id']
            variants = test_info['variants']
            
            if not variants:
                logger.warning(f"Aucune variante trouvée pour le test '{test_name}'")
                return None
                
            # Vérifier si l'utilisateur est déjà assigné
            check_query = """
            SELECT variant FROM personalization_ab_test_assignments
            WHERE test_id = :test_id AND user_id = :user_id
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(check_query), {
                    "test_id": test_id,
                    "user_id": user_id
                })
                assignment = result.fetchone()
                
                if assignment:
                    return assignment[0]
                
                # Si l'utilisateur n'est pas assigné, l'assigner à une variante
                variant = self._assign_variant(user_id, variants)
                
                # Enregistrer l'assignation
                query = """
                INSERT INTO personalization_ab_test_assignments (
                    test_id, user_id, variant
                ) VALUES (
                    :test_id, :user_id, :variant
                )
                """
                
                conn.execute(text(query), {
                    "test_id": test_id,
                    "user_id": user_id,
                    "variant": variant
                })
                
                conn.commit()
                
                logger.debug(f"Utilisateur {user_id} assigné à la variante '{variant}' du test '{test_name}'")
                
                return variant
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la variante: {e}")
            return None
    
    def record_test_result(self, user_id: int, test_name: str, 
                          metrics: Dict[str, float]) -> bool:
        """
        Enregistre les résultats d'un test pour un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            test_name: Nom du test A/B
            metrics: Métriques à enregistrer
            
        Returns:
            True si l'enregistrement a réussi, False sinon
        """
        try:
            if self.engine is None:
                logger.warning("Connexion à la base de données non disponible")
                return False
                
            # Vérifier si le test existe
            test_info = self._get_test_info(test_name)
            
            if not test_info:
                logger.warning(f"Test '{test_name}' non trouvé")
                return False
                
            test_id = test_info['id']
            
            # Vérifier si l'utilisateur est assigné à ce test
            check_query = """
            SELECT id, variant FROM personalization_ab_test_assignments
            WHERE test_id = :test_id AND user_id = :user_id
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(check_query), {
                    "test_id": test_id,
                    "user_id": user_id
                })
                assignment = result.fetchone()
                
                if not assignment:
                    logger.warning(f"Utilisateur {user_id} non assigné au test '{test_name}'")
                    return False
                
                assignment_id = assignment[0]
                variant = assignment[1]
                
                # Mettre à jour les résultats du test
                query = """
                UPDATE personalization_ab_tests
                SET results = jsonb_set(
                    COALESCE(results, '{}'::jsonb),
                    ARRAY[:variant], 
                    COALESCE(results->:variant, '{}'::jsonb) || :metrics::jsonb
                )
                WHERE id = :test_id
                """
                
                conn.execute(text(query), {
                    "test_id": test_id,
                    "variant": variant,
                    "metrics": json.dumps(metrics)
                })
                
                conn.commit()
                
                logger.debug(f"Résultats enregistrés pour l'utilisateur {user_id}, test '{test_name}', variante '{variant}'")
                
                return True
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement des résultats du test: {e}")
            return False
    
    def get_test_results(self, test_name: str) -> Dict[str, Any]:
        """
        Récupère les résultats d'un test A/B.
        
        Args:
            test_name: Nom du test A/B
            
        Returns:
            Résultats du test
        """
        try:
            if self.engine is None:
                logger.warning("Connexion à la base de données non disponible")
                return {
                    'success': False,
                    'error': 'database_connection_error'
                }
                
            # Vérifier si le test existe
            test_info = self._get_test_info(test_name)
            
            if not test_info:
                return {
                    'success': False,
                    'error': 'test_not_found'
                }
                
            test_id = test_info['id']
            variants = test_info['variants']
            status = test_info['status']
            results = test_info.get('results', {})
            
            # Récupérer le nombre d'utilisateurs par variante
            query = """
            SELECT variant, COUNT(*) as user_count
            FROM personalization_ab_test_assignments
            WHERE test_id = :test_id
            GROUP BY variant
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(query), {"test_id": test_id})
                
                variant_counts = {}
                for row in result:
                    variant_counts[row[0]] = row[1]
            
            # Formater les résultats
            formatted_results = []
            
            for variant in variants:
                variant_results = results.get(variant, {})
                
                # Calculer les métriques agrégées
                metrics = {}
                if variant_results:
                    for metric_name, values in variant_results.items():
                        if isinstance(values, list):
                            metrics[metric_name] = {
                                'mean': np.mean(values),
                                'median': np.median(values),
                                'std': np.std(values),
                                'min': min(values),
                                'max': max(values),
                                'count': len(values)
                            }
                        else:
                            metrics[metric_name] = values
                
                formatted_results.append({
                    'variant': variant,
                    'user_count': variant_counts.get(variant, 0),
                    'metrics': metrics
                })
            
            return {
                'success': True,
                'test_name': test_name,
                'status': status,
                'variants': formatted_results,
                'start_date': test_info.get('start_date'),
                'end_date': test_info.get('end_date')
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des résultats du test: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def end_test(self, test_name: str) -> Dict[str, Any]:
        """
        Termine un test A/B.
        
        Args:
            test_name: Nom du test A/B
            
        Returns:
            Résultats du test
        """
        try:
            if self.engine is None:
                logger.warning("Connexion à la base de données non disponible")
                return {
                    'success': False,
                    'error': 'database_connection_error'
                }
                
            # Vérifier si le test existe
            test_info = self._get_test_info(test_name)
            
            if not test_info:
                return {
                    'success': False,
                    'error': 'test_not_found'
                }
                
            if test_info['status'] != 'active':
                return {
                    'success': False,
                    'error': 'test_already_completed'
                }
                
            test_id = test_info['id']
            
            # Mettre à jour le statut du test
            query = """
            UPDATE personalization_ab_tests
            SET status = 'completed', end_date = CURRENT_TIMESTAMP
            WHERE id = :test_id
            """
            
            with self.engine.connect() as conn:
                conn.execute(text(query), {"test_id": test_id})
                conn.commit()
            
            # Vider le cache des tests actifs
            self._active_tests_cache = None
            
            logger.info(f"Test A/B '{test_name}' terminé")
            
            # Renvoyer les résultats finaux
            return self.get_test_results(test_name)
        except Exception as e:
            logger.error(f"Erreur lors de la fin du test: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_active_tests(self) -> List[Dict[str, Any]]:
        """
        Récupère la liste des tests A/B actifs.
        
        Returns:
            Liste des tests actifs
        """
        try:
            if self.engine is None:
                logger.warning("Connexion à la base de données non disponible")
                return []
                
            # Utiliser le cache si disponible
            if self._active_tests_cache is not None:
                return self._active_tests_cache
                
            # Requête pour récupérer les tests actifs
            query = """
            SELECT 
                id, test_name, description, variants, 
                start_date, end_date
            FROM personalization_ab_tests
            WHERE status = 'active'
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                
                tests = []
                for row in result:
                    tests.append({
                        'id': row[0],
                        'name': row[1],
                        'description': row[2],
                        'variants': json.loads(row[3]) if row[3] else [],
                        'start_date': row[4].isoformat() if row[4] else None,
                        'end_date': row[5].isoformat() if row[5] else None
                    })
                
                # Mettre à jour le cache
                self._active_tests_cache = tests
                
                return tests
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des tests actifs: {e}")
            return []
    
    def _get_test_info(self, test_name: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les informations d'un test A/B.
        
        Args:
            test_name: Nom du test A/B
            
        Returns:
            Informations sur le test ou None si le test n'existe pas
        """
        try:
            if self.engine is None:
                logger.warning("Connexion à la base de données non disponible")
                return None
                
            # Vérifier dans le cache des tests actifs
            if self._active_tests_cache is not None:
                for test in self._active_tests_cache:
                    if test['name'] == test_name:
                        return {
                            'id': test['id'],
                            'variants': test['variants'],
                            'status': 'active',
                            'start_date': test['start_date'],
                            'end_date': test['end_date']
                        }
            
            # Requête pour récupérer les informations du test
            query = """
            SELECT 
                id, variants, status, results, 
                start_date, end_date
            FROM personalization_ab_tests
            WHERE test_name = :test_name
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(query), {"test_name": test_name})
                row = result.fetchone()
                
                if not row:
                    return None
                
                return {
                    'id': row[0],
                    'variants': json.loads(row[1]) if row[1] else [],
                    'status': row[2],
                    'results': json.loads(row[3]) if row[3] else {},
                    'start_date': row[4].isoformat() if row[4] else None,
                    'end_date': row[5].isoformat() if row[5] else None
                }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des informations du test: {e}")
            return None
    
    def _assign_variant(self, user_id: int, variants: List[str]) -> str:
        """
        Assigne un utilisateur à une variante.
        
        Args:
            user_id: ID de l'utilisateur
            variants: Liste des variantes disponibles
            
        Returns:
            Nom de la variante assignée
        """
        # Méthode d'assignation
        if self.assignment_method == 'deterministic':
            # Assignation déterministe basée sur un hash du user_id
            seed = hashlib.md5(str(user_id).encode()).hexdigest()
            seed_value = int(seed, 16) % 100  # Valeur entre 0 et 99
            
            # Réserver les premiers % pour le groupe de contrôle
            control_threshold = int(self.control_group_size * 100)
            
            if seed_value < control_threshold:
                return variants[0]  # Premier variant = contrôle
            else:
                # Répartir les autres variantes uniformément
                variant_index = 1 + ((seed_value - control_threshold) * (len(variants) - 1)) // (100 - control_threshold)
                return variants[min(variant_index, len(variants) - 1)]
        else:
            # Assignation aléatoire
            if random.random() < self.control_group_size:
                return variants[0]  # Premier variant = contrôle
            else:
                # Choisir aléatoirement parmi les autres variantes
                return random.choice(variants[1:]) if len(variants) > 1 else variants[0]
