#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gestion du démarrage à froid pour les nouveaux utilisateurs.

Ce module fournit des solutions pour les nouveaux utilisateurs
n'ayant pas encore d'historique de préférences.
"""

import logging
import random
from typing import Dict, List, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)

class ColdStartHandler:
    """
    Gestionnaire pour le problème du démarrage à froid.
    
    Cette classe fournit des méthodes pour traiter les nouveaux utilisateurs
    sans historique d'interactions suffisant.
    """
    
    def __init__(self, data_loader):
        """
        Initialise le gestionnaire de démarrage à froid.
        
        Args:
            data_loader: Chargeur de données
        """
        self.data_loader = data_loader
        self.min_interactions = 5  # Nombre minimal d'interactions pour sortir du démarrage à froid
    
    def is_new_user(self, user_id: str) -> bool:
        """
        Détermine si un utilisateur est nouveau (peu ou pas d'historique).
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            bool: True si l'utilisateur est nouveau, False sinon
        """
        # Compter le nombre d'interactions de l'utilisateur
        feedback_count = self.data_loader.get_user_feedback_count(user_id)
        
        return feedback_count < self.min_interactions
    
    def get_default_weights(self, user_id: str, job_id: Optional[int] = None, 
                          candidate_id: Optional[int] = None,
                          original_weights: Dict[str, float] = None) -> Dict[str, float]:
        """
        Fournit des poids par défaut pour un nouvel utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            job_id: ID de l'offre d'emploi (optionnel)
            candidate_id: ID du candidat (optionnel)
            original_weights: Poids originaux
            
        Returns:
            Poids par défaut
        """
        if not original_weights:
            original_weights = {
                'skills': 0.4,
                'experience': 0.3,
                'education': 0.2,
                'certifications': 0.1
            }
        
        # Pour les nouveaux utilisateurs, on peut introduire une petite variation
        # pour explorer différentes combinaisons de poids
        default_weights = {}
        
        # Générer un identifiant unique basé sur l'ID utilisateur
        # pour avoir une variation cohérente entre les appels
        seed = int(''.join([str(ord(c)) for c in user_id])[:8])
        random.seed(seed)
        
        # Ajouter une petite variation aléatoire aux poids
        for key, value in original_weights.items():
            # Variation de +/- 20% maximum
            variation = random.uniform(-0.1, 0.1)
            default_weights[key] = max(0.05, value + variation)
        
        # Normaliser les poids pour qu'ils somment à 1
        total = sum(default_weights.values())
        for key in default_weights:
            default_weights[key] /= total
        
        # Si un job_id est fourni, on peut adapter les poids en fonction
        # des caractéristiques du job
        if job_id:
            job_data = self.data_loader.get_job_details(job_id) or {}
            
            # Exemple: Si le job met l'accent sur les compétences techniques
            if job_data.get('tech_focus', False):
                # Augmenter l'importance des compétences
                default_weights['skills'] += 0.05
                # Réduire l'importance des autres critères
                for key in default_weights:
                    if key != 'skills':
                        default_weights[key] -= 0.05 / 3
            
            # Normaliser à nouveau
            total = sum(default_weights.values())
            for key in default_weights:
                default_weights[key] /= total
        
        return default_weights
    
    def diversify_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Diversifie les résultats pour les nouveaux utilisateurs.
        
        Args:
            results: Résultats originaux
            
        Returns:
            Résultats diversifiés
        """
        if not results or len(results) <= 5:
            return results
        
        # Pour les nouveaux utilisateurs, on cherche à favoriser la diversité
        # pour explorer différents types d'emplois
        
        # Séparer les résultats en groupes de 3
        top_results = results[:3]  # Garder les 3 premiers résultats inchangés
        remaining_results = results[3:]
        
        # Mélanger le reste des résultats avec un seed fixe pour la cohérence
        random.seed(42)
        random.shuffle(remaining_results)
        
        # Répartir les résultats restants en groupes par catégorie
        categories = {}
        for result in remaining_results:
            job_id = result.get('job_id')
            if not job_id:
                continue
            
            job_data = self.data_loader.get_job_details(job_id) or {}
            category = job_data.get('category', 'other')
            
            if category not in categories:
                categories[category] = []
            
            categories[category].append(result)
        
        # Prendre un élément de chaque catégorie à tour de rôle
        diversified_results = top_results.copy()
        category_keys = list(categories.keys())
        
        while category_keys and len(diversified_results) < len(results):
            for category in list(category_keys):  # Copie pour pouvoir modifier pendant l'itération
                if categories[category]:
                    diversified_results.append(categories[category].pop(0))
                    
                    # Si plus d'éléments dans cette catégorie, la retirer
                    if not categories[category]:
                        category_keys.remove(category)
                        
                # Si assez de résultats, arrêter
                if len(diversified_results) >= len(results):
                    break
        
        # Ajouter les résultats restants si nécessaire
        remaining_flat = [item for sublist in categories.values() for item in sublist]
        diversified_results.extend(remaining_flat[:len(results) - len(diversified_results)])
        
        return diversified_results
    
    def suggest_exploration_jobs(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Suggère des offres d'emploi pour l'exploration.
        
        Args:
            user_id: ID de l'utilisateur
            limit: Nombre maximum de suggestions
            
        Returns:
            Liste des suggestions
        """
        # Récupérer les emplois populaires ou diversifiés
        popular_jobs = self.data_loader.get_popular_jobs(limit=20)
        
        if not popular_jobs:
            return []
        
        # Pour un nouvel utilisateur, sélectionner un échantillon diversifié
        selected_jobs = []
        
        # Regrouper par catégorie
        jobs_by_category = {}
        for job in popular_jobs:
            category = job.get('category', 'other')
            if category not in jobs_by_category:
                jobs_by_category[category] = []
            jobs_by_category[category].append(job)
        
        # Prendre un job de chaque catégorie
        for category, jobs in jobs_by_category.items():
            if len(selected_jobs) < limit:
                selected_jobs.append(random.choice(jobs))
        
        # Si pas assez de catégories, compléter avec des jobs au hasard
        while len(selected_jobs) < limit and popular_jobs:
            remaining_jobs = [job for job in popular_jobs if job not in selected_jobs]
            if not remaining_jobs:
                break
            selected_jobs.append(random.choice(remaining_jobs))
        
        return selected_jobs
    
    def get_popular_preferences(self) -> Dict[str, Any]:
        """
        Récupère les préférences populaires pour les nouveaux utilisateurs.
        
        Returns:
            Préférences populaires
        """
        # Préférences par défaut basées sur les utilisateurs existants
        return {
            'matching_weights': {
                'skills': 0.45,
                'experience': 0.25,
                'education': 0.2,
                'certifications': 0.1
            },
            'job_preferences': {
                'categories': ['Software Development', 'Data Science', 'Management'],
                'contract_types': ['CDI', 'Freelance'],
                'locations': ['Paris', 'Lyon', 'Remote'],
                'remote': 0.5  # Préférence moyenne pour le télétravail
            },
            'notification_preferences': {
                'email': True,
                'push': False,
                'frequency': 'daily'
            }
        }
