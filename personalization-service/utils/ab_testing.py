#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gestionnaire de tests A/B pour le service de personnalisation

Ce module permet de configurer et exécuter des tests A/B pour évaluer
l'efficacité des différentes stratégies de personnalisation.
"""

import logging
import json
import redis
import random
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ABTestManager:
    """
    Classe pour gérer les tests A/B des fonctionnalités de personnalisation
    """
    
    def __init__(self, redis_client: redis.Redis):
        """
        Initialise le gestionnaire de tests A/B
        
        Args:
            redis_client: Instance de client Redis
        """
        self.redis_client = redis_client
        
        # Configuration par défaut des tests A/B
        self.default_tests = {
            'personalization_test': {
                'enabled': True,
                'groups': [
                    {'name': 'control', 'weight': 0.2},   # 20% des utilisateurs sans personnalisation
                    {'name': 'variant_a', 'weight': 0.4}, # 40% des utilisateurs avec personnalisation standard
                    {'name': 'variant_b', 'weight': 0.4}  # 40% des utilisateurs avec personnalisation avancée
                ],
                'start_date': datetime.now().isoformat(),
                'end_date': (datetime.now() + timedelta(days=30)).isoformat()
            }
        }
        
        # Cache des tests A/B
        self.tests_cache = None
        self.last_cache_update = None
        self.cache_ttl = 1800  # 30 minutes
        
        # Cache des assignations utilisateur
        self.user_assignments = {}
    
    def get_test_config(self, test_id: str = 'personalization_test') -> Optional[Dict[str, Any]]:
        """
        Récupère la configuration d'un test A/B
        
        Args:
            test_id: Identifiant du test
            
        Returns:
            Dict: Configuration du test ou None si non trouvé
        """
        # Charger les configurations de test si elles ne sont pas en cache
        if not self.tests_cache or (datetime.now() - self.last_cache_update).total_seconds() > self.cache_ttl:
            self._load_test_configs()
        
        return self.tests_cache.get(test_id)
    
    def _load_test_configs(self) -> None:
        """
        Charge les configurations des tests A/B depuis Redis
        """
        try:
            # Essayer de récupérer les configurations depuis Redis
            configs_json = self.redis_client.get('ab_test_configs')
            
            if configs_json:
                self.tests_cache = json.loads(configs_json)
            else:
                # Si pas de configuration en Redis, utiliser les configurations par défaut
                self.tests_cache = self.default_tests.copy()
                # Sauvegarder les configurations par défaut dans Redis
                self.redis_client.set('ab_test_configs', json.dumps(self.tests_cache))
            
            self.last_cache_update = datetime.now()
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement des configurations de tests A/B: {str(e)}", exc_info=True)
            # En cas d'erreur, utiliser les configurations par défaut
            self.tests_cache = self.default_tests.copy()
            self.last_cache_update = datetime.now()
    
    def get_user_group(self, user_id: str, test_id: str = 'personalization_test') -> str:
        """
        Détermine le groupe A/B auquel appartient un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            test_id: Identifiant du test
            
        Returns:
            str: Nom du groupe A/B ('control', 'variant_a', etc.)
        """
        # Vérifier si l'utilisateur a déjà été assigné à un groupe
        cache_key = f"user_group:{user_id}:{test_id}"
        if cache_key in self.user_assignments:
            return self.user_assignments[cache_key]
        
        # Vérifier si l'assignation est déjà en cache Redis
        group = self.redis_client.get(cache_key)
        if group:
            group = group.decode('utf-8')
            self.user_assignments[cache_key] = group
            return group
        
        # Récupérer la configuration du test
        test_config = self.get_test_config(test_id)
        if not test_config:
            # Si pas de test, retourner le groupe par défaut
            return 'variant_a'
        
        # Vérifier si le test est actif
        if not test_config.get('enabled', True):
            return 'variant_a'
        
        # Vérifier si le test est dans sa période d'activité
        now = datetime.now()
        start_date = datetime.fromisoformat(test_config.get('start_date', '2000-01-01T00:00:00'))
        end_date = datetime.fromisoformat(test_config.get('end_date', '2100-01-01T00:00:00'))
        
        if now < start_date or now > end_date:
            return 'variant_a'
        
        # Déterminer le groupe de l'utilisateur de manière déterministe
        groups = test_config.get('groups', [])
        if not groups:
            return 'variant_a'
        
        # Calculer un hash déterministe pour l'utilisateur
        hash_input = f"{user_id}:{test_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        random_value = (hash_value % 1000) / 1000.0  # Valeur entre 0 et 1
        
        # Attribuer un groupe en fonction des poids
        cumulative_weight = 0.0
        for group in groups:
            cumulative_weight += group.get('weight', 0.0)
            if random_value <= cumulative_weight:
                selected_group = group.get('name', 'variant_a')
                break
        else:
            selected_group = 'variant_a'
        
        # Sauvegarder l'assignation dans Redis pour la cohérence entre les requêtes
        self.redis_client.set(cache_key, selected_group)
        self.user_assignments[cache_key] = selected_group
        
        return selected_group
    
    def record_experiment_result(self, user_id: str, test_id: str, event_type: str, value: Union[int, float, bool] = 1) -> bool:
        """
        Enregistre un résultat d'expérience A/B
        
        Args:
            user_id: ID de l'utilisateur
            test_id: Identifiant du test
            event_type: Type d'événement ('click', 'conversion', etc.)
            value: Valeur associée à l'événement
            
        Returns:
            bool: True si succès, False sinon
        """
        try:
            # Récupérer le groupe de l'utilisateur
            group = self.get_user_group(user_id, test_id)
            
            # Enregistrer l'événement dans Redis
            event_data = {
                'user_id': user_id,
                'test_id': test_id,
                'group': group,
                'event_type': event_type,
                'value': value,
                'timestamp': datetime.now().isoformat()
            }
            
            # Ajouter à une liste pour l'analyse ultérieure
            event_key = f"ab_test_events:{test_id}:{event_type}"
            self.redis_client.rpush(event_key, json.dumps(event_data))
            
            # Mettre à jour les compteurs
            counter_key = f"ab_test_counters:{test_id}:{group}:{event_type}"
            self.redis_client.incr(counter_key)
            
            if isinstance(value, (int, float)) and value != 1:
                # Si une valeur numérique est fournie, mettre à jour la somme
                sum_key = f"ab_test_sums:{test_id}:{group}:{event_type}"
                self.redis_client.incrbyfloat(sum_key, value)
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement du résultat d'expérience: {str(e)}", exc_info=True)
            return False
    
    def get_experiment_stats(self, test_id: str, event_type: str) -> Dict[str, Dict[str, Any]]:
        """
        Récupère les statistiques d'une expérience A/B
        
        Args:
            test_id: Identifiant du test
            event_type: Type d'événement
            
        Returns:
            Dict: Statistiques par groupe
        """
        try:
            # Récupérer la configuration du test
            test_config = self.get_test_config(test_id)
            if not test_config:
                return {}
            
            groups = [group.get('name') for group in test_config.get('groups', [])]
            if not groups:
                return {}
            
            stats = {}
            
            for group in groups:
                # Compteurs de base
                counter_key = f"ab_test_counters:{test_id}:{group}:{event_type}"
                count = int(self.redis_client.get(counter_key) or 0)
                
                # Sommes pour les valeurs numériques
                sum_key = f"ab_test_sums:{test_id}:{group}:{event_type}"
                value_sum = float(self.redis_client.get(sum_key) or 0.0)
                
                # Statistiques du groupe
                stats[group] = {
                    'count': count,
                    'sum': value_sum,
                    'average': value_sum / count if count > 0 else 0.0
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques d'expérience: {str(e)}", exc_info=True)
            return {}
    
    def save_test_config(self, test_id: str, config: Dict[str, Any]) -> bool:
        """
        Sauvegarde la configuration d'un test A/B
        
        Args:
            test_id: Identifiant du test
            config: Configuration du test
            
        Returns:
            bool: True si succès, False sinon
        """
        try:
            # Charger les configurations existantes
            if not self.tests_cache:
                self._load_test_configs()
            
            # Mettre à jour la configuration du test
            self.tests_cache[test_id] = config
            
            # Sauvegarder dans Redis
            self.redis_client.set('ab_test_configs', json.dumps(self.tests_cache))
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de la configuration de test: {str(e)}", exc_info=True)
            return False
    
    def reset_user_assignment(self, user_id: str, test_id: str = 'personalization_test') -> bool:
        """
        Réinitialise l'assignation d'un utilisateur pour un test A/B
        
        Args:
            user_id: ID de l'utilisateur
            test_id: Identifiant du test
            
        Returns:
            bool: True si succès, False sinon
        """
        try:
            # Supprimer l'assignation du cache local
            cache_key = f"user_group:{user_id}:{test_id}"
            if cache_key in self.user_assignments:
                del self.user_assignments[cache_key]
            
            # Supprimer l'assignation de Redis
            self.redis_client.delete(cache_key)
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la réinitialisation de l'assignation utilisateur: {str(e)}", exc_info=True)
            return False
