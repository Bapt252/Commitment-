import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class PreferenceScoreCalculator:
    """Calcule des scores de préférence dynamiques basés sur le comportement utilisateur."""
    
    def __init__(self, recency_decay=0.9, action_weights=None, time_window_days=30):
        """
        Initialise le calculateur de scores de préférence.
        
        Args:
            recency_decay (float): Facteur de décroissance avec le temps (0-1)
            action_weights (dict): Poids des différents types d'action
            time_window_days (int): Fenêtre de temps pour l'analyse (jours)
        """
        self.recency_decay = recency_decay
        self.time_window_days = time_window_days
        
        # Poids par défaut pour différents types d'action
        self.action_weights = action_weights or {
            'view_job': 1,
            'apply_job': 5,
            'save_job': 2,
            'search': 0.5,
            'view_company': 0.8
        }
    
    def calculate_preference_scores(self, user_actions, categories=None, now=None):
        """
        Calcule les scores de préférence pour différentes catégories/tags.
        
        Args:
            user_actions (list): Liste de dictionnaires représentant les actions utilisateur
            categories (list, optional): Liste des catégories à évaluer
            now (datetime, optional): Date actuelle pour les calculs de récence
            
        Returns:
            dict: Scores de préférence par utilisateur et catégorie
        """
        if not user_actions:
            return {}
            
        now = now or datetime.now()
        cutoff_date = now - timedelta(days=self.time_window_days)
        
        # Convertir en DataFrame pour faciliter l'analyse
        df = pd.DataFrame(user_actions)
        
        # Filtrer les actions dans la fenêtre temporelle
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df[df['timestamp'] >= cutoff_date]
        
        if df.empty:
            return {}
        
        # S'assurer que les colonnes nécessaires sont présentes
        required_cols = ['user_id', 'action_type']
        if not all(col in df.columns for col in required_cols):
            missing = [col for col in required_cols if col not in df.columns]
            logger.error(f"Colonnes manquantes dans les données d'action: {missing}")
            return {}
        
        # Calculer les scores par utilisateur
        preference_scores = {}
        
        for user_id, user_df in df.groupby('user_id'):
            # Calculer les scores pour cet utilisateur
            user_scores = self._calculate_user_scores(user_df, categories, now)
            preference_scores[user_id] = user_scores
            
        return preference_scores
    
    def _calculate_user_scores(self, user_df, categories, now):
        """
        Calcule les scores de préférence pour un utilisateur spécifique.
        
        Args:
            user_df (DataFrame): Actions d'un utilisateur spécifique
            categories (list): Liste des catégories à évaluer
            now (datetime): Date actuelle
            
        Returns:
            dict: Scores de préférence par catégorie pour cet utilisateur
        """
        scores = {}
        
        # Si 'category' ou 'tag' est dans les colonnes, utiliser pour calculer les scores
        if 'category' in user_df.columns:
            category_col = 'category'
        elif 'job_category' in user_df.columns:
            category_col = 'job_category'
        elif 'tag' in user_df.columns:
            category_col = 'tag'
        else:
            # Si pas de catégorie/tag disponible, créer un score global
            return {'global': self._calculate_global_score(user_df, now)}
            
        # Si les catégories ne sont pas spécifiées, utiliser celles des données
        if not categories:
            categories = user_df[category_col].unique().tolist()
            
        # Calculer le score pour chaque catégorie
        for category in categories:
            category_df = user_df[user_df[category_col] == category]
            if not category_df.empty:
                scores[category] = self._calculate_category_score(category_df, now)
            else:
                scores[category] = 0.0
                
        # Normaliser les scores
        total_score = sum(scores.values())
        if total_score > 0:
            for category in scores:
                scores[category] /= total_score
                
        return scores
    
    def _calculate_category_score(self, category_df, now):
        """
        Calcule le score pour une catégorie spécifique.
        
        Args:
            category_df (DataFrame): Actions pour une catégorie spécifique
            now (datetime): Date actuelle
            
        Returns:
            float: Score pour cette catégorie
        """
        score = 0.0
        
        for _, row in category_df.iterrows():
            # Poids de l'action
            action_weight = self.action_weights.get(row['action_type'], 1.0)
            
            # Facteur de récence (décroissance exponentielle)
            if 'timestamp' in row:
                days_ago = (now - row['timestamp']).days
                recency_factor = self.recency_decay ** days_ago
            else:
                recency_factor = 1.0
                
            # Facteur d'engagement (si disponible)
            engagement_factor = 1.0
            if 'duration' in row:
                # Plus de 2 minutes = engagement maximal
                engagement_factor = min(1.0, row['duration'] / 120.0)
            
            # Facteur explicite (si disponible)
            explicit_factor = 1.0
            if 'rating' in row:
                explicit_factor = row['rating'] / 5.0  # Supposant une échelle de 1-5
                
            # Combiner les facteurs
            action_score = action_weight * recency_factor * engagement_factor * explicit_factor
            
            # Ajouter au score total
            score += action_score
            
        return score
    
    def _calculate_global_score(self, user_df, now):
        """
        Calcule un score global basé sur l'activité générale.
        
        Args:
            user_df (DataFrame): Actions d'un utilisateur spécifique
            now (datetime): Date actuelle
            
        Returns:
            float: Score global d'activité
        """
        score = 0.0
        
        for _, row in user_df.iterrows():
            # Poids de l'action
            action_weight = self.action_weights.get(row['action_type'], 1.0)
            
            # Facteur de récence
            if 'timestamp' in row:
                days_ago = (now - row['timestamp']).days
                recency_factor = self.recency_decay ** days_ago
            else:
                recency_factor = 1.0
                
            # Ajouter au score total
            score += action_weight * recency_factor
            
        return score
    
    def update_preference_scores(self, existing_scores, new_actions, now=None):
        """
        Met à jour les scores de préférence existants avec de nouvelles actions.
        
        Args:
            existing_scores (dict): Scores de préférence existants
            new_actions (list): Nouvelles actions à intégrer
            now (datetime, optional): Date actuelle
            
        Returns:
            dict: Scores de préférence mis à jour
        """
        now = now or datetime.now()
        
        # Calculer les scores pour les nouvelles actions
        new_scores = self.calculate_preference_scores(new_actions, now=now)
        
        # Fusionner avec les scores existants
        updated_scores = existing_scores.copy()
        
        for user_id, user_new_scores in new_scores.items():
            if user_id in updated_scores:
                user_existing_scores = updated_scores[user_id]
                
                # Appliquer la décroissance temporelle aux scores existants
                for category in user_existing_scores:
                    # Supposer que les scores existants datent d'environ 1 jour
                    user_existing_scores[category] *= self.recency_decay
                
                # Ajouter les nouveaux scores
                for category, score in user_new_scores.items():
                    if category in user_existing_scores:
                        user_existing_scores[category] += score
                    else:
                        user_existing_scores[category] = score
                        
                # Renormaliser
                total_score = sum(user_existing_scores.values())
                if total_score > 0:
                    for category in user_existing_scores:
                        user_existing_scores[category] /= total_score
            else:
                # Nouvel utilisateur
                updated_scores[user_id] = user_new_scores
                
        return updated_scores