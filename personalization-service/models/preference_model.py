#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modèle de préférences utilisateur pour la personnalisation.

Ce module gère les préférences des utilisateurs et permet de personnaliser
les résultats de matching en fonction de ces préférences.
"""

import logging
from typing import Dict, List, Any, Optional
import json
import numpy as np
from datetime import datetime
from sklearn.cluster import KMeans

logger = logging.getLogger(__name__)

class PreferenceModel:
    """
    Gestion des préférences utilisateur pour la personnalisation.
    
    Ce modèle maintient les préférences des utilisateurs et les utilise
    pour personnaliser les résultats de matching.
    """
    
    def __init__(self, data_loader):
        """
        Initialise le modèle de préférences.
        
        Args:
            data_loader: Chargeur de données
        """
        self.data_loader = data_loader
        self.user_segments = {}  # Cache des segments utilisateurs
        self.MAX_HISTORY = 100  # Nombre maximum d'actions à conserver dans l'historique
        
        # Paramètres pour la segmentation d'utilisateurs
        self.n_clusters = 5  # Nombre de segments
        self.segments_description = {
            0: "Chercheurs actifs tech/dev",
            1: "Professionnels senior management",
            2: "Explorateurs passifs",
            3: "Jeunes diplômés polyvalents",
            4: "Experts techniques spécialisés"
        }
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Récupère les préférences d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Préférences de l'utilisateur
        """
        # Récupérer les préférences de la base de données ou du cache
        preferences = self.data_loader.get_user_preferences(user_id)
        
        if not preferences:
            # Créer des préférences par défaut si aucune n'existe
            preferences = {
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
        
        return preferences
    
    def save_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """
        Sauvegarde les préférences d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            preferences: Préférences à sauvegarder
            
        Returns:
            bool: True si succès, False sinon
        """
        # Mettre à jour la date de dernière mise à jour
        preferences['last_updated'] = datetime.now().isoformat()
        
        # Sauvegarder dans la base de données
        success = self.data_loader.save_user_preferences(user_id, preferences)
        
        # Invalider le segment utilisateur dans le cache si existant
        if user_id in self.user_segments:
            del self.user_segments[user_id]
        
        return success
    
    def get_personalized_weights(self, user_id: str, job_id: Optional[int] = None, 
                               candidate_id: Optional[int] = None,
                               original_weights: Dict[str, float] = None) -> Dict[str, float]:
        """
        Calcule les poids personnalisés pour un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            job_id: ID de l'offre d'emploi (optionnel)
            candidate_id: ID du candidat (optionnel)
            original_weights: Poids originaux
            
        Returns:
            Poids personnalisés
        """
        if not original_weights:
            original_weights = {
                'skills': 0.4,
                'experience': 0.3,
                'education': 0.2,
                'certifications': 0.1
            }
        
        # Récupérer les préférences de l'utilisateur
        preferences = self.get_user_preferences(user_id)
        
        # Si des poids personnalisés sont déjà définis, les utiliser
        if preferences and 'matching_weights' in preferences:
            custom_weights = preferences['matching_weights']
            
            # Vérifier que toutes les clés nécessaires sont présentes
            for key in original_weights:
                if key not in custom_weights:
                    custom_weights[key] = original_weights[key]
            
            # Normaliser les poids pour qu'ils somment à 1
            total = sum(custom_weights.values())
            if total > 0:
                for key in custom_weights:
                    custom_weights[key] /= total
            
            return custom_weights
        
        # Si pas de poids personnalisés, utiliser les poids originaux
        return original_weights
    
    def rerank_results(self, user_id: str, results: List[Dict[str, Any]], 
                     search_query: str = '', context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Réordonne les résultats en fonction des préférences de l'utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            results: Résultats originaux
            search_query: Requête de recherche
            context: Contexte de la recherche
            
        Returns:
            Résultats réordonnés
        """
        if not results:
            return []
        
        # Récupérer les préférences de l'utilisateur
        preferences = self.get_user_preferences(user_id)
        
        # Si pas de préférences définies, retourner les résultats inchangés
        if not preferences or 'job_preferences' not in preferences:
            return results
        
        job_preferences = preferences.get('job_preferences', {})
        interaction_history = preferences.get('interaction_history', [])
        
        # Calculer les scores pour chaque résultat
        reranked_results = []
        for result in results:
            job_id = result.get('job_id')
            if not job_id:
                reranked_results.append({'result': result, 'score': 0.0})
                continue
            
            job_data = self.data_loader.get_job_details(job_id) or {}
            
            # Score initial (par exemple, le score de matching)
            initial_score = result.get('score', 0.5)
            
            # Calculer un score de préférence basé sur les préférences utilisateur
            preference_score = 0.0
            
            # Préférences de catégorie
            preferred_categories = job_preferences.get('categories', [])
            if preferred_categories and job_data.get('category'):
                if job_data.get('category') in preferred_categories:
                    preference_score += 0.2
            
            # Préférences de type de contrat
            preferred_contracts = job_preferences.get('contract_types', [])
            if preferred_contracts and job_data.get('contract_type'):
                if job_data.get('contract_type') in preferred_contracts:
                    preference_score += 0.15
            
            # Préférences de lieu
            preferred_locations = job_preferences.get('locations', [])
            if preferred_locations and job_data.get('location'):
                if job_data.get('location') in preferred_locations:
                    preference_score += 0.15
            
            # Préférence télétravail
            remote_preference = job_preferences.get('remote')
            if remote_preference is not None and job_data.get('remote') is not None:
                if job_data.get('remote') == remote_preference:
                    preference_score += 0.1
            
            # Analyser l'historique d'interaction pour les jobs similaires
            if interaction_history:
                for interaction in interaction_history:
                    if interaction.get('action') in ['like', 'apply', 'bookmark']:
                        similar_job_id = interaction.get('job_id')
                        if similar_job_id and similar_job_id != job_id:
                            similar_job = self.data_loader.get_job_details(similar_job_id) or {}
                            
                            # Si catégorie similaire
                            if similar_job.get('category') == job_data.get('category'):
                                preference_score += 0.1
                            
                            # Si entreprise similaire
                            if similar_job.get('company') == job_data.get('company'):
                                preference_score += 0.1
            
            # Limiter le score de préférence à [0, 0.5]
            preference_score = min(0.5, preference_score)
            
            # Score final combiné (50% score initial, 50% score de préférence)
            final_score = initial_score * 0.5 + preference_score
            
            reranked_results.append({'result': result, 'score': final_score})
        
        # Trier par score final et extraire seulement les résultats
        reranked_results.sort(key=lambda x: x['score'], reverse=True)
        return [item['result'] for item in reranked_results]
    
    def update_from_feedback(self, feedback_data: Dict[str, Any]) -> None:
        """
        Met à jour le modèle de préférences à partir d'un feedback.
        
        Args:
            feedback_data: Données de feedback
        """
        user_id = feedback_data.get('user_id')
        if not user_id:
            return
        
        # Récupérer les préférences actuelles
        preferences = self.get_user_preferences(user_id)
        
        # Mettre à jour l'historique d'interaction
        interaction_history = preferences.get('interaction_history', [])
        
        # Créer une nouvelle entrée pour l'interaction
        new_interaction = {
            'timestamp': feedback_data.get('timestamp', datetime.now().isoformat()),
            'action': feedback_data.get('action', ''),
            'job_id': feedback_data.get('job_id'),
            'candidate_id': feedback_data.get('candidate_id'),
            'context': feedback_data.get('context', {})
        }
        
        # Ajouter l'interaction au début de l'historique
        interaction_history.insert(0, new_interaction)
        
        # Limiter la taille de l'historique
        if len(interaction_history) > self.MAX_HISTORY:
            interaction_history = interaction_history[:self.MAX_HISTORY]
        
        preferences['interaction_history'] = interaction_history
        
        # Mise à jour des poids de matching en fonction des actions
        if feedback_data.get('action') in ['like', 'apply', 'bookmark', 'dislike']:
            job_id = feedback_data.get('job_id')
            
            if job_id:
                # Récupérer les détails du job
                job_data = self.data_loader.get_job_details(job_id) or {}
                
                # Examiner quel aspect du job a pu motiver l'action (compétences, expérience, etc.)
                self._update_weights_from_job(preferences, job_data, feedback_data.get('action'))
        
        # Mise à jour des préférences d'emploi
        self._update_job_preferences(preferences, feedback_data)
        
        # Sauvegarder les préférences mises à jour
        self.save_user_preferences(user_id, preferences)
        
        # Invalider le segment utilisateur dans le cache
        if user_id in self.user_segments:
            del self.user_segments[user_id]
    
    def _update_weights_from_job(self, preferences: Dict[str, Any], job_data: Dict[str, Any], action: str) -> None:
        """
        Met à jour les poids de matching en fonction des caractéristiques d'un job.
        
        Args:
            preferences: Préférences utilisateur
            job_data: Données du job
            action: Type d'action (like, dislike, etc.)
        """
        # Initialiser les poids de matching si nécessaire
        if 'matching_weights' not in preferences:
            preferences['matching_weights'] = {
                'skills': 0.4,
                'experience': 0.3,
                'education': 0.2,
                'certifications': 0.1
            }
        
        weights = preferences['matching_weights']
        
        # Ajustement des poids en fonction de l'action et des caractéristiques du job
        adjustment = 0.05 if action in ['like', 'apply', 'bookmark'] else -0.03
        
        # Analyser le job pour déterminer quel aspect pourrait être important
        if 'skills_importance' in job_data and job_data['skills_importance'] == 'high':
            weights['skills'] += adjustment
        
        if 'experience_required' in job_data and job_data['experience_required'] >= 5:
            weights['experience'] += adjustment
        
        if 'education_required' in job_data and job_data['education_required'] in ['master', 'phd']:
            weights['education'] += adjustment
        
        if 'certifications_required' in job_data and job_data['certifications_required']:
            weights['certifications'] += adjustment
        
        # Normaliser les poids pour qu'ils somment à 1
        total = sum(weights.values())
        if total > 0:
            for key in weights:
                weights[key] /= total
    
    def _update_job_preferences(self, preferences: Dict[str, Any], feedback_data: Dict[str, Any]) -> None:
        """
        Met à jour les préférences d'emploi en fonction d'un feedback.
        
        Args:
            preferences: Préférences utilisateur
            feedback_data: Données de feedback
        """
        # Initialiser les préférences d'emploi si nécessaire
        if 'job_preferences' not in preferences:
            preferences['job_preferences'] = {
                'categories': [],
                'contract_types': [],
                'locations': [],
                'remote': None
            }
        
        job_preferences = preferences['job_preferences']
        
        # Ne mettre à jour les préférences que pour les actions positives
        if feedback_data.get('action') not in ['like', 'apply', 'bookmark']:
            return
        
        job_id = feedback_data.get('job_id')
        if not job_id:
            return
        
        # Récupérer les détails du job
        job_data = self.data_loader.get_job_details(job_id) or {}
        
        # Mise à jour des catégories préférées
        if 'category' in job_data and job_data['category']:
            category = job_data['category']
            if category not in job_preferences['categories']:
                job_preferences['categories'].append(category)
                # Limiter à 5 catégories maximum
                if len(job_preferences['categories']) > 5:
                    job_preferences['categories'].pop(0)
        
        # Mise à jour des types de contrat préférés
        if 'contract_type' in job_data and job_data['contract_type']:
            contract_type = job_data['contract_type']
            if contract_type not in job_preferences['contract_types']:
                job_preferences['contract_types'].append(contract_type)
                # Limiter à 3 types de contrat maximum
                if len(job_preferences['contract_types']) > 3:
                    job_preferences['contract_types'].pop(0)
        
        # Mise à jour des lieux préférés
        if 'location' in job_data and job_data['location']:
            location = job_data['location']
            if location not in job_preferences['locations']:
                job_preferences['locations'].append(location)
                # Limiter à 5 lieux maximum
                if len(job_preferences['locations']) > 5:
                    job_preferences['locations'].pop(0)
        
        # Mise à jour de la préférence de télétravail
        if 'remote' in job_data:
            # Simple moyenne mobile
            if job_preferences['remote'] is None:
                job_preferences['remote'] = job_data['remote']
            else:
                # 70% ancien + 30% nouveau
                job_preferences['remote'] = job_preferences['remote'] * 0.7 + job_data['remote'] * 0.3
    
    def get_user_segment(self, user_id: str) -> Dict[str, Any]:
        """
        Détermine le segment auquel appartient un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Segment de l'utilisateur (ID et description)
        """
        # Vérifier si le segment est en cache
        if user_id in self.user_segments:
            return self.user_segments[user_id]
        
        # Récupérer l'historique de feedback de l'utilisateur
        user_feedback = self.data_loader.get_user_feedback(user_id)
        
        if not user_feedback:
            # Pas assez de données pour une segmentation, utiliser segment par défaut
            segment = {
                'id': 2,  # Segment "Explorateurs passifs"
                'name': self.segments_description[2],
                'confidence': 0.0
            }
            self.user_segments[user_id] = segment
            return segment
        
        # Extraire les caractéristiques pour la segmentation
        features = {
            'like_ratio': 0,
            'apply_ratio': 0,
            'bookmark_ratio': 0,
            'view_count': 0,
            'tech_ratio': 0,
            'management_ratio': 0,
            'senior_ratio': 0,
            'remote_ratio': 0
        }
        
        # Compter les différents types d'actions
        action_counts = {'like': 0, 'apply': 0, 'bookmark': 0, 'view': 0, 'total': 0}
        job_counts = {'tech': 0, 'management': 0, 'senior': 0, 'remote': 0, 'total': 0}
        
        for feedback in user_feedback:
            action = feedback.get('action', '')
            job_id = feedback.get('job_id')
            
            # Compter les actions
            action_counts['total'] += 1
            if action in action_counts:
                action_counts[action] += 1
            
            # Analyser les caractéristiques du job
            if job_id:
                job_data = self.data_loader.get_job_details(job_id) or {}
                job_counts['total'] += 1
                
                # Catégorie Tech
                category = job_data.get('category', '').lower()
                if 'tech' in category or 'dev' in category or 'software' in category:
                    job_counts['tech'] += 1
                
                # Catégorie Management
                if 'manager' in category or 'director' in category or 'lead' in category:
                    job_counts['management'] += 1
                
                # Niveau Senior
                experience = job_data.get('experience_level', '').lower()
                if 'senior' in experience or 'expert' in experience or job_data.get('experience_years', 0) >= 5:
                    job_counts['senior'] += 1
                
                # Télétravail
                if job_data.get('remote', False):
                    job_counts['remote'] += 1
        
        # Calculer les ratios
        if action_counts['total'] > 0:
            features['like_ratio'] = action_counts['like'] / action_counts['total']
            features['apply_ratio'] = action_counts['apply'] / action_counts['total']
            features['bookmark_ratio'] = action_counts['bookmark'] / action_counts['total']
            features['view_count'] = action_counts['view']
        
        if job_counts['total'] > 0:
            features['tech_ratio'] = job_counts['tech'] / job_counts['total']
            features['management_ratio'] = job_counts['management'] / job_counts['total']
            features['senior_ratio'] = job_counts['senior'] / job_counts['total']
            features['remote_ratio'] = job_counts['remote'] / job_counts['total']
        
        # Convertir en vecteur pour la segmentation
        feature_vector = np.array([
            features['like_ratio'],
            features['apply_ratio'],
            features['bookmark_ratio'],
            min(1.0, features['view_count'] / 50),  # Normaliser à 50 vues max
            features['tech_ratio'],
            features['management_ratio'],
            features['senior_ratio'],
            features['remote_ratio']
        ]).reshape(1, -1)
        
        # Centres de clusters prédéfinis (déterminés par l'analyse de données)
        # Ces centres représentent les profils-types
        cluster_centers = np.array([
            # Chercheurs actifs tech/dev
            [0.5, 0.3, 0.4, 0.8, 0.8, 0.1, 0.3, 0.6],
            # Professionnels senior management
            [0.3, 0.2, 0.5, 0.4, 0.2, 0.7, 0.8, 0.3],
            # Explorateurs passifs
            [0.2, 0.1, 0.3, 0.5, 0.4, 0.3, 0.2, 0.3],
            # Jeunes diplômés polyvalents
            [0.6, 0.4, 0.3, 0.9, 0.5, 0.2, 0.1, 0.5],
            # Experts techniques spécialisés
            [0.4, 0.3, 0.6, 0.6, 0.9, 0.2, 0.6, 0.8]
        ])
        
        # Calculer la distance à chaque centre
        distances = np.sqrt(((feature_vector - cluster_centers) ** 2).sum(axis=1))
        
        # Trouver le cluster le plus proche
        closest_cluster = np.argmin(distances)
        
        # Calculer un score de confiance (inverse de la distance normalisée)
        min_dist = np.min(distances)
        max_dist = np.max(distances)
        confidence = 1.0
        if max_dist > min_dist:
            confidence = 1.0 - (min_dist / max_dist)
        
        # Créer l'objet segment
        segment = {
            'id': int(closest_cluster),
            'name': self.segments_description[closest_cluster],
            'confidence': float(confidence),
            'features': {k: float(v) for k, v in features.items()}
        }
        
        # Mettre en cache
        self.user_segments[user_id] = segment
        
        return segment
