#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Détection de la dérive temporelle des préférences utilisateur.

Ce module détecte les changements dans les préférences des utilisateurs
au fil du temps et adapte les modèles en conséquence.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class TemporalDriftDetector:
    """
    Détecteur de la dérive temporelle des préférences utilisateur.
    
    Cette classe surveille l'évolution des préférences utilisateur
    et détecte quand elles changent significativement.
    """
    
    def __init__(self, max_age_days: int = 30):
        """
        Initialise le détecteur de dérive temporelle.
        
        Args:
            max_age_days: Âge maximum en jours avant de considérer un modèle comme obsolète
        """
        self.max_age_days = max_age_days
        self.drift_thresholds = {
            'interaction_count': 50,  # Nombre d'interactions pour détecter une dérive
            'new_category_ratio': 0.3,  # Ratio de nouvelles catégories pour détecter une dérive
            'action_change_threshold': 0.2  # Seuil de changement dans les actions pour détecter une dérive
        }
    
    def has_drifted(self, user_id: str, preferences: Optional[Dict[str, Any]] = None) -> bool:
        """
        Détermine si les préférences d'un utilisateur ont dérivé.
        
        Args:
            user_id: ID de l'utilisateur
            preferences: Préférences actuelles (optionnel)
            
        Returns:
            bool: True si dérive détectée, False sinon
        """
        if not preferences:
            # Si les préférences ne sont pas fournies, on considère qu'il n'y a pas de dérive
            return False
        
        # Vérifier la date de dernière mise à jour
        last_updated = preferences.get('last_updated')
        if last_updated:
            try:
                last_update_date = datetime.fromisoformat(last_updated)
                current_date = datetime.now()
                
                # Si plus vieux que max_age_days, considérer comme obsolète
                if (current_date - last_update_date).days > self.max_age_days:
                    logger.info(f"Dérive temporelle détectée pour l'utilisateur {user_id}: modèle obsolète")
                    return True
            except (ValueError, TypeError):
                # Si date invalide, ignorer cette vérification
                pass
        
        # Vérifier l'historique d'interaction
        interaction_history = preferences.get('interaction_history', [])
        
        if len(interaction_history) >= self.drift_thresholds['interaction_count']:
            # Diviser l'historique en deux moitiés
            half_point = len(interaction_history) // 2
            recent_interactions = interaction_history[:half_point]  # Plus récentes en premier
            old_interactions = interaction_history[half_point:]
            
            # Détecter un changement dans les catégories d'emploi
            if self._detect_category_drift(recent_interactions, old_interactions):
                logger.info(f"Dérive temporelle détectée pour l'utilisateur {user_id}: changement de catégories")
                return True
            
            # Détecter un changement dans les actions
            if self._detect_action_drift(recent_interactions, old_interactions):
                logger.info(f"Dérive temporelle détectée pour l'utilisateur {user_id}: changement d'actions")
                return True
        
        return False
    
    def _detect_category_drift(self, recent_interactions: List[Dict[str, Any]], 
                              old_interactions: List[Dict[str, Any]]) -> bool:
        """
        Détecte une dérive dans les catégories d'emploi.
        
        Args:
            recent_interactions: Interactions récentes
            old_interactions: Anciennes interactions
            
        Returns:
            bool: True si dérive détectée, False sinon
        """
        # Extraire les catégories des interactions récentes et anciennes
        recent_categories = set()
        old_categories = set()
        
        for interaction in recent_interactions:
            job_id = interaction.get('job_id')
            if job_id:
                category = interaction.get('job_category')
                if category:
                    recent_categories.add(category)
        
        for interaction in old_interactions:
            job_id = interaction.get('job_id')
            if job_id:
                category = interaction.get('job_category')
                if category:
                    old_categories.add(category)
        
        # Si pas assez de catégories, pas de dérive
        if not recent_categories or not old_categories:
            return False
        
        # Calculer le ratio de nouvelles catégories
        new_categories = recent_categories - old_categories
        new_category_ratio = len(new_categories) / len(recent_categories)
        
        return new_category_ratio >= self.drift_thresholds['new_category_ratio']
    
    def _detect_action_drift(self, recent_interactions: List[Dict[str, Any]], 
                           old_interactions: List[Dict[str, Any]]) -> bool:
        """
        Détecte une dérive dans les actions utilisateur.
        
        Args:
            recent_interactions: Interactions récentes
            old_interactions: Anciennes interactions
            
        Returns:
            bool: True si dérive détectée, False sinon
        """
        # Compter les types d'actions dans les interactions récentes et anciennes
        recent_actions = {'like': 0, 'dislike': 0, 'apply': 0, 'bookmark': 0, 'view': 0, 'total': 0}
        old_actions = {'like': 0, 'dislike': 0, 'apply': 0, 'bookmark': 0, 'view': 0, 'total': 0}
        
        for interaction in recent_interactions:
            action = interaction.get('action', '')
            recent_actions['total'] += 1
            if action in recent_actions:
                recent_actions[action] += 1
        
        for interaction in old_interactions:
            action = interaction.get('action', '')
            old_actions['total'] += 1
            if action in old_actions:
                old_actions[action] += 1
        
        # Si pas assez d'actions, pas de dérive
        if recent_actions['total'] == 0 or old_actions['total'] == 0:
            return False
        
        # Calculer les ratios d'actions
        recent_ratios = {}
        old_ratios = {}
        
        for action in ['like', 'dislike', 'apply', 'bookmark', 'view']:
            recent_ratios[action] = recent_actions[action] / recent_actions['total']
            old_ratios[action] = old_actions[action] / old_actions['total']
        
        # Calculer la distance entre les ratios
        distance = 0
        for action in ['like', 'dislike', 'apply', 'bookmark', 'view']:
            distance += abs(recent_ratios[action] - old_ratios[action])
        
        # Normaliser la distance
        distance /= 5  # 5 types d'actions
        
        return distance >= self.drift_thresholds['action_change_threshold']
    
    def reset_user_model(self, user_id: str, preferences: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Réinitialise le modèle d'un utilisateur après une dérive.
        
        Args:
            user_id: ID de l'utilisateur
            preferences: Préférences actuelles (optionnel)
            
        Returns:
            Préférences réinitialisées
        """
        if not preferences:
            # Si les préférences ne sont pas fournies, retourner un modèle vide
            return {
                'matching_weights': {
                    'skills': 0.4,
                    'experience': 0.3,
                    'education': 0.2,
                    'certifications': 0.1
                },
                'job_preferences': {
                    'categories': [],
                    'contract_types': [],
                    'locations': [],
                    'remote': None
                },
                'notification_preferences': {
                    'email': True,
                    'push': False,
                    'frequency': 'daily'
                },
                'interaction_history': [],
                'last_updated': datetime.now().isoformat()
            }
        
        # Conserver l'historique d'interaction récent seulement
        interaction_history = preferences.get('interaction_history', [])
        recent_history = interaction_history[:min(20, len(interaction_history))]  # Garder les 20 interactions les plus récentes
        
        # Réinitialiser les poids et préférences, mais garder l'historique récent
        reset_preferences = {
            'matching_weights': {
                'skills': 0.4,
                'experience': 0.3,
                'education': 0.2,
                'certifications': 0.1
            },
            'job_preferences': {
                'categories': [],
                'contract_types': [],
                'locations': [],
                'remote': None
            },
            'notification_preferences': preferences.get('notification_preferences', {
                'email': True,
                'push': False,
                'frequency': 'daily'
            }),
            'interaction_history': recent_history,
            'last_updated': datetime.now().isoformat()
        }
        
        # Reconstruire les préférences basées sur l'historique récent
        self._rebuild_preferences_from_history(reset_preferences)
        
        logger.info(f"Modèle réinitialisé pour l'utilisateur {user_id} après détection de dérive temporelle")
        
        return reset_preferences
    
    def _rebuild_preferences_from_history(self, preferences: Dict[str, Any]) -> None:
        """
        Reconstruit les préférences à partir de l'historique récent.
        
        Args:
            preferences: Préférences à mettre à jour
        """
        interaction_history = preferences.get('interaction_history', [])
        
        if not interaction_history:
            return
        
        # Analyser l'historique pour reconstruire les préférences
        categories = {}
        contract_types = {}
        locations = {}
        remote_count = 0
        remote_total = 0
        
        for interaction in interaction_history:
            if interaction.get('action') in ['like', 'apply', 'bookmark']:
                # Extraire les informations du job si disponibles
                job_category = interaction.get('job_category')
                job_contract = interaction.get('job_contract_type')
                job_location = interaction.get('job_location')
                job_remote = interaction.get('job_remote')
                
                # Mettre à jour les compteurs
                if job_category:
                    categories[job_category] = categories.get(job_category, 0) + 1
                
                if job_contract:
                    contract_types[job_contract] = contract_types.get(job_contract, 0) + 1
                
                if job_location:
                    locations[job_location] = locations.get(job_location, 0) + 1
                
                if job_remote is not None:
                    remote_count += 1
                    remote_total += 1 if job_remote else 0
        
        # Mettre à jour les préférences d'emploi
        job_preferences = preferences.get('job_preferences', {})
        
        # Top 3 catégories
        if categories:
            top_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:3]
            job_preferences['categories'] = [cat for cat, _ in top_categories]
        
        # Top 2 types de contrat
        if contract_types:
            top_contracts = sorted(contract_types.items(), key=lambda x: x[1], reverse=True)[:2]
            job_preferences['contract_types'] = [contract for contract, _ in top_contracts]
        
        # Top 3 lieux
        if locations:
            top_locations = sorted(locations.items(), key=lambda x: x[1], reverse=True)[:3]
            job_preferences['locations'] = [loc for loc, _ in top_locations]
        
        # Préférence télétravail
        if remote_count > 0:
            job_preferences['remote'] = remote_total / remote_count
        
        preferences['job_preferences'] = job_preferences
