#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modèle de filtrage collaboratif pour la personnalisation.

Ce module implémente un système de recommandation basé sur le filtrage
collaboratif pour personnaliser les résultats de matching.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
import logging
from scipy.spatial.distance import cosine
import json

logger = logging.getLogger(__name__)

class CollaborativeFilter:
    """
    Système de recommandation basé sur le filtrage collaboratif.
    
    Ce système identifie les utilisateurs similaires et utilise leurs
    préférences pour personnaliser les recommandations.
    """
    
    def __init__(self, data_loader):
        """
        Initialise le filtre collaboratif.
        
        Args:
            data_loader: Chargeur de données
        """
        self.data_loader = data_loader
        self.user_vectors = {}  # Cache des vecteurs utilisateurs
        self.similarity_cache = {}  # Cache des similarités entre utilisateurs
        
    def _build_user_vector(self, user_id: str) -> np.ndarray:
        """
        Construit un vecteur de caractéristiques pour un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            np.ndarray: Vecteur de caractéristiques
        """
        # Récupérer l'historique de feedback de l'utilisateur
        user_feedback = self.data_loader.get_user_feedback(user_id)
        
        if not user_feedback:
            return np.zeros(20)  # Vecteur vide si pas de feedback
        
        # Construire un vecteur basé sur les actions et les catégories
        features = {
            # Compteurs d'actions
            'like_count': 0,
            'dislike_count': 0,
            'bookmark_count': 0,
            'apply_count': 0,
            'view_count': 0,
            
            # Caractéristiques des emplois
            'tech_jobs': 0,
            'management_jobs': 0,
            'finance_jobs': 0,
            'marketing_jobs': 0,
            'other_jobs': 0,
            
            # Niveaux d'expérience
            'junior_jobs': 0,
            'mid_jobs': 0,
            'senior_jobs': 0,
            
            # Modes de travail
            'remote_jobs': 0,
            'office_jobs': 0,
            'hybrid_jobs': 0,
            
            # Types de contrat
            'permanent_jobs': 0,
            'contract_jobs': 0,
            'internship_jobs': 0,
            'freelance_jobs': 0,
        }
        
        # Remplir le vecteur avec les feedbacks
        for feedback in user_feedback:
            action = feedback.get('action', '')
            job_id = feedback.get('job_id')
            context = feedback.get('context', {})
            
            # Incrémenter les compteurs d'actions
            if action == 'like':
                features['like_count'] += 1
            elif action == 'dislike':
                features['dislike_count'] += 1
            elif action == 'bookmark':
                features['bookmark_count'] += 1
            elif action == 'apply':
                features['apply_count'] += 1
            elif action == 'view':
                features['view_count'] += 1
            
            # Extraire les caractéristiques du job si disponibles
            if job_id:
                job_data = self.data_loader.get_job_details(job_id) or {}
                
                # Catégorie
                category = job_data.get('category', '').lower()
                if 'tech' in category or 'it' in category or 'software' in category:
                    features['tech_jobs'] += 1
                elif 'manager' in category or 'director' in category or 'lead' in category:
                    features['management_jobs'] += 1
                elif 'finance' in category or 'accounting' in category:
                    features['finance_jobs'] += 1
                elif 'marketing' in category or 'communication' in category:
                    features['marketing_jobs'] += 1
                else:
                    features['other_jobs'] += 1
                
                # Niveau d'expérience
                experience = job_data.get('experience_level', '').lower()
                if 'junior' in experience or 'entry' in experience:
                    features['junior_jobs'] += 1
                elif 'senior' in experience or 'expert' in experience:
                    features['senior_jobs'] += 1
                else:
                    features['mid_jobs'] += 1
                
                # Mode de travail
                work_mode = job_data.get('work_mode', '').lower()
                if 'remote' in work_mode:
                    features['remote_jobs'] += 1
                elif 'office' in work_mode or 'on-site' in work_mode:
                    features['office_jobs'] += 1
                else:
                    features['hybrid_jobs'] += 1
                
                # Type de contrat
                contract_type = job_data.get('contract_type', '').lower()
                if 'permanent' in contract_type or 'cdi' in contract_type:
                    features['permanent_jobs'] += 1
                elif 'contract' in contract_type or 'cdd' in contract_type:
                    features['contract_jobs'] += 1
                elif 'internship' in contract_type or 'stage' in contract_type:
                    features['internship_jobs'] += 1
                elif 'freelance' in contract_type:
                    features['freelance_jobs'] += 1
        
        # Convertir le dictionnaire en vecteur numpy
        vector = np.array(list(features.values()))
        
        # Normaliser le vecteur si non-nul
        if vector.sum() > 0:
            vector = vector / vector.sum()
        
        return vector
    
    def calculate_user_similarity(self, user_id1: str, user_id2: str) -> float:
        """
        Calcule la similarité entre deux utilisateurs.
        
        Args:
            user_id1: Premier utilisateur
            user_id2: Deuxième utilisateur
            
        Returns:
            float: Score de similarité [0-1]
        """
        # Vérifier le cache de similarité
        cache_key = f"{user_id1}:{user_id2}"
        if cache_key in self.similarity_cache:
            return self.similarity_cache[cache_key]
        
        # Récupérer ou construire les vecteurs utilisateurs
        if user_id1 not in self.user_vectors:
            self.user_vectors[user_id1] = self._build_user_vector(user_id1)
        
        if user_id2 not in self.user_vectors:
            self.user_vectors[user_id2] = self._build_user_vector(user_id2)
        
        vector1 = self.user_vectors[user_id1]
        vector2 = self.user_vectors[user_id2]
        
        # Si l'un des vecteurs est nul, similarité nulle
        if np.sum(vector1) == 0 or np.sum(vector2) == 0:
            similarity = 0.0
        else:
            # Calculer la similarité cosinus inversée (1 - cosine distance)
            similarity = 1.0 - cosine(vector1, vector2)
            
            # Gestion des erreurs (NaN)
            if np.isnan(similarity):
                similarity = 0.0
        
        # Mettre en cache la similarité
        self.similarity_cache[cache_key] = similarity
        self.similarity_cache[f"{user_id2}:{user_id1}"] = similarity  # Symétrique
        
        return similarity
    
    def get_similar_users(self, user_id: str, limit: int = 10, min_similarity: float = 0.3) -> List[Dict[str, Any]]:
        """
        Trouve les utilisateurs similaires à un utilisateur donné.
        
        Args:
            user_id: ID de l'utilisateur
            limit: Nombre maximum d'utilisateurs à retourner
            min_similarity: Similarité minimum requise
            
        Returns:
            Liste des utilisateurs similaires triés par similarité
        """
        # Récupérer tous les IDs utilisateurs
        all_user_ids = self.data_loader.get_all_user_ids()
        
        # Calculer la similarité avec chaque utilisateur
        similar_users = []
        for other_id in all_user_ids:
            if other_id == user_id:
                continue
            
            similarity = self.calculate_user_similarity(user_id, other_id)
            
            if similarity >= min_similarity:
                similar_users.append({
                    'user_id': other_id,
                    'similarity': similarity
                })
        
        # Trier par similarité décroissante et limiter
        similar_users = sorted(similar_users, key=lambda x: x['similarity'], reverse=True)[:limit]
        
        return similar_users
    
    def get_similar_users_weights(self, user_id: str, job_id: Optional[int] = None, 
                                candidate_id: Optional[int] = None,
                                original_weights: Dict[str, float] = None) -> Dict[str, float]:
        """
        Calcule les poids personnalisés basés sur des utilisateurs similaires.
        
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
        
        # Trouver les utilisateurs similaires
        similar_users = self.get_similar_users(user_id, limit=5, min_similarity=0.3)
        
        if not similar_users:
            return original_weights
        
        # Récupérer les poids personnalisés de chaque utilisateur similaire
        all_weights = []
        total_similarity = 0.0
        
        for similar_user in similar_users:
            other_id = similar_user['user_id']
            similarity = similar_user['similarity']
            
            # Récupérer les préférences de l'utilisateur similaire
            user_preferences = self.data_loader.get_user_preferences(other_id)
            
            if user_preferences and 'matching_weights' in user_preferences:
                all_weights.append({
                    'weights': user_preferences['matching_weights'],
                    'similarity': similarity
                })
                total_similarity += similarity
        
        if not all_weights or total_similarity == 0:
            return original_weights
        
        # Calculer les poids pondérés par similarité
        personalized_weights = {}
        for key in original_weights.keys():
            weighted_sum = sum(w['weights'].get(key, original_weights[key]) * w['similarity'] for w in all_weights)
            personalized_weights[key] = weighted_sum / total_similarity
        
        # Normaliser les poids pour qu'ils somment à 1
        total = sum(personalized_weights.values())
        if total > 0:
            for key in personalized_weights:
                personalized_weights[key] /= total
        
        return personalized_weights
    
    def rerank_results(self, user_id: str, results: List[Dict[str, Any]], 
                     search_query: str = '', context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Réordonne les résultats en fonction des préférences des utilisateurs similaires.
        
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
        
        # Trouver les utilisateurs similaires
        similar_users = self.get_similar_users(user_id, limit=5, min_similarity=0.3)
        
        if not similar_users:
            return results
        
        # Calculer les scores pour chaque résultat
        reranked_results = []
        for result in results:
            job_id = result.get('job_id')
            if not job_id:
                reranked_results.append({'result': result, 'score': 0.0})
                continue
            
            # Score initial (par exemple, le score de matching)
            initial_score = result.get('score', 0.5)
            
            # Calculer le score d'affinité basé sur les utilisateurs similaires
            affinity_score = 0.0
            total_similarity = 0.0
            
            for similar_user in similar_users:
                other_id = similar_user['user_id']
                similarity = similar_user['similarity']
                
                # Récupérer les feedbacks de l'utilisateur similaire pour ce job
                other_feedback = self.data_loader.get_user_job_feedback(other_id, job_id)
                
                if other_feedback:
                    # Calculer un score d'affinité basé sur les actions
                    action_scores = {
                        'like': 1.0,
                        'apply': 1.0,
                        'bookmark': 0.8,
                        'view': 0.3,
                        'dislike': -0.5,
                        'ignore': -0.2
                    }
                    
                    for feedback in other_feedback:
                        action = feedback.get('action', '')
                        if action in action_scores:
                            affinity_score += similarity * action_scores[action]
                            total_similarity += similarity
            
            # Score final combiné
            final_score = initial_score
            if total_similarity > 0:
                # Normaliser le score d'affinité
                normalized_affinity = affinity_score / total_similarity
                
                # Combiner le score initial et le score d'affinité (70% initial, 30% affinité)
                final_score = initial_score * 0.7 + (normalized_affinity + 1) / 2 * 0.3
            
            reranked_results.append({'result': result, 'score': final_score})
        
        # Trier par score final et extraire seulement les résultats
        reranked_results.sort(key=lambda x: x['score'], reverse=True)
        return [item['result'] for item in reranked_results]
    
    def update_from_feedback(self, feedback_data: Dict[str, Any]) -> None:
        """
        Met à jour le modèle à partir d'un nouveau feedback.
        
        Args:
            feedback_data: Données de feedback
        """
        user_id = feedback_data.get('user_id')
        if not user_id:
            return
        
        # Invalider le cache de vecteur pour cet utilisateur
        if user_id in self.user_vectors:
            del self.user_vectors[user_id]
        
        # Invalider le cache de similarité pour cet utilisateur
        keys_to_remove = []
        for key in self.similarity_cache:
            if key.startswith(f"{user_id}:") or key.endswith(f":{user_id}"):
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            if key in self.similarity_cache:
                del self.similarity_cache[key]
