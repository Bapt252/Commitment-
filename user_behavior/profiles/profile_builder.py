import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class UserProfileBuilder:
    """Construit des profils utilisateur enrichis basés sur leur comportement."""
    
    def __init__(self, recency_weight=0.5, frequency_weight=0.3, engagement_weight=0.2):
        """
        Initialise le constructeur de profils.
        
        Args:
            recency_weight (float): Poids de la récence dans le score
            frequency_weight (float): Poids de la fréquence dans le score
            engagement_weight (float): Poids de l'engagement dans le score
        """
        self.recency_weight = recency_weight
        self.frequency_weight = frequency_weight
        self.engagement_weight = engagement_weight
        
    def build_user_profiles(self, user_actions, user_data=None):
        """
        Construit des profils utilisateur enrichis à partir des actions et données.
        
        Args:
            user_actions (list): Liste de dictionnaires représentant les actions utilisateur
            user_data (dict, optional): Dictionnaire des données de base utilisateur
                
        Returns:
            dict: Profils utilisateur enrichis
        """
        # Convertir en DataFrame pour faciliter l'analyse
        actions_df = pd.DataFrame(user_actions)
        actions_df['timestamp'] = pd.to_datetime(actions_df['timestamp'])
        
        # Date actuelle pour les calculs de récence
        now = datetime.now()
        
        # Initialiser le dictionnaire de profils
        user_profiles = {}
        
        # Transformer user_data en dictionnaire user_id -> data
        user_data_dict = {}
        if user_data:
            for user in user_data:
                user_data_dict[user['user_id']] = user
        
        # Regrouper les actions par utilisateur
        for user_id, user_actions_df in actions_df.groupby('user_id'):
            # Récupérer les données de base si disponibles
            base_data = user_data_dict.get(user_id, {})
            
            # Construire le profil
            profile = self._build_profile(user_id, user_actions_df, base_data, now)
            user_profiles[user_id] = profile
            
        logger.info(f"Profils construits pour {len(user_profiles)} utilisateurs")
        return user_profiles
    
    def _build_profile(self, user_id, actions_df, base_data, now):
        """
        Construit un profil utilisateur à partir de ses actions.
        
        Args:
            user_id (str): ID de l'utilisateur
            actions_df (DataFrame): Actions de l'utilisateur
            base_data (dict): Données de base utilisateur
            now (datetime): Date actuelle pour les calculs de récence
            
        Returns:
            dict: Profil utilisateur enrichi
        """
        # Données de base
        profile = {
            'user_id': user_id,
            'name': base_data.get('name', ''),
            'email': base_data.get('email', ''),
            'created_at': base_data.get('created_at', ''),
            'profile_completion': base_data.get('profile_completion', 0),
        }
        
        # Statistiques générales
        profile['action_count'] = len(actions_df)
        
        if not actions_df.empty:
            profile['first_action'] = actions_df['timestamp'].min().isoformat()
            profile['last_action'] = actions_df['timestamp'].max().isoformat()
            profile['days_active'] = (actions_df['timestamp'].max() - actions_df['timestamp'].min()).days + 1
        else:
            profile['first_action'] = None
            profile['last_action'] = None
            profile['days_active'] = 0
        
        # Répartition des types d'action
        action_types = actions_df['action_type'].value_counts().to_dict()
        profile['action_types'] = action_types
        
        # Nombre de vues de fiches de poste
        profile['job_view_count'] = action_types.get('view_job', 0)
        
        # Nombre de candidatures
        profile['application_count'] = action_types.get('apply_job', 0)
        
        # Taux de conversion (vues -> candidatures)
        if profile['job_view_count'] > 0:
            profile['conversion_rate'] = profile['application_count'] / profile['job_view_count']
        else:
            profile['conversion_rate'] = 0.0
        
        # Calcul des sessions
        if not actions_df.empty:
            profile.update(self._calculate_sessions(actions_df))
        else:
            profile['session_count'] = 0
            profile['avg_session_duration'] = 0
            profile['avg_actions_per_session'] = 0
        
        # Extraire les préférences de l'utilisateur
        if 'item_id' in actions_df.columns:
            profile['preferences'] = self._extract_preferences(actions_df)
        
        # Calculer les scores RFE (Recency, Frequency, Engagement)
        profile.update(self._calculate_rfe_scores(actions_df, now))
        
        return profile
    
    def _calculate_sessions(self, actions_df, session_timeout=30):
        """
        Regroupe les actions en sessions et calcule des statistiques.
        
        Args:
            actions_df (DataFrame): Actions de l'utilisateur
            session_timeout (int): Temps d'inactivité (minutes) pour considérer une nouvelle session
            
        Returns:
            dict: Statistiques de session
        """
        if len(actions_df) < 2:
            return {
                'session_count': 1 if len(actions_df) == 1 else 0,
                'avg_session_duration': 0,
                'avg_actions_per_session': len(actions_df)
            }
            
        # Trier par timestamp
        df = actions_df.sort_values('timestamp')
        
        # Calculer le temps entre les actions
        df['time_diff'] = df['timestamp'].diff()
        
        # Identifier les démarrages de session (time_diff > timeout ou première action)
        session_start = df['time_diff'].isnull() | (df['time_diff'] > pd.Timedelta(minutes=session_timeout))
        df['session_id'] = session_start.cumsum()
        
        # Calculer les statistiques par session
        sessions = df.groupby('session_id').agg({
            'timestamp': ['min', 'max', 'count']
        })
        
        sessions.columns = ['start_time', 'end_time', 'action_count']
        sessions['duration'] = sessions['end_time'] - sessions['start_time']
        
        # Statistiques globales
        session_count = len(sessions)
        total_duration = sessions['duration'].sum().total_seconds() / 60  # en minutes
        avg_duration = total_duration / session_count if session_count > 0 else 0
        avg_actions = sessions['action_count'].mean() if session_count > 0 else 0
        
        return {
            'session_count': session_count,
            'avg_session_duration': avg_duration,
            'avg_actions_per_session': avg_actions
        }
    
    def _extract_preferences(self, actions_df):
        """
        Extrait les préférences utilisateur basées sur ses interactions.
        
        Args:
            actions_df (DataFrame): Actions de l'utilisateur
            
        Returns:
            dict: Préférences utilisateur
        """
        preferences = {}
        
        # Si les données incluent des informations sur les offres d'emploi consultées
        if 'item_id' in actions_df.columns and 'job_category' in actions_df.columns:
            # Préférences par catégorie
            category_counts = actions_df['job_category'].value_counts()
            preferences['categories'] = category_counts.to_dict()
            
            # Top catégories
            preferences['top_categories'] = category_counts.nlargest(3).index.tolist()
            
        # Si les données incluent la durée de consultation
        if 'duration' in actions_df.columns and 'item_id' in actions_df.columns:
            # Items consultés le plus longtemps
            item_duration = actions_df.groupby('item_id')['duration'].sum()
            preferences['top_items_by_duration'] = item_duration.nlargest(5).index.tolist()
        
        return preferences
    
    def _calculate_rfe_scores(self, actions_df, now):
        """
        Calcule les scores RFE (Recency, Frequency, Engagement).
        
        Args:
            actions_df (DataFrame): Actions de l'utilisateur
            now (datetime): Date actuelle
            
        Returns:
            dict: Scores RFE
        """
        if actions_df.empty:
            return {
                'recency_score': 0,
                'frequency_score': 0,
                'engagement_score': 0,
                'rfe_score': 0
            }
            
        # Récence: jours depuis la dernière action (inversé et normalisé)
        last_action = actions_df['timestamp'].max()
        days_since_last = (now - last_action).days
        # Plus le nombre est petit, plus c'est récent, donc meilleur le score
        recency_score = max(0, 1 - (days_since_last / 30))  # Normalisé sur 30 jours
        
        # Fréquence: nombre d'actions sur les 30 derniers jours
        recent_df = actions_df[actions_df['timestamp'] > (now - timedelta(days=30))]
        action_count = len(recent_df)
        # Normaliser (supposant qu'une action par jour est "idéal")
        frequency_score = min(1, action_count / 30)
        
        # Engagement: variété d'actions et temps passé
        engagement_factors = []
        
        # Variété des types d'action
        action_variety = len(actions_df['action_type'].unique()) / 5  # Supposant 5 types possibles
        engagement_factors.append(min(1, action_variety))
        
        # Taux de conversion (si applicable)
        job_views = len(actions_df[actions_df['action_type'] == 'view_job'])
        applications = len(actions_df[actions_df['action_type'] == 'apply_job'])
        if job_views > 0:
            conversion = applications / job_views
            engagement_factors.append(min(1, conversion * 2))  # Un taux de 50% = score de 1
        
        # Durée moyenne des sessions (si calculée)
        if 'session_id' in actions_df.columns:
            sessions = actions_df.groupby('session_id').agg({
                'timestamp': ['min', 'max']
            })
            sessions.columns = ['start_time', 'end_time']
            sessions['duration'] = (sessions['end_time'] - sessions['start_time']).dt.total_seconds() / 60
            avg_duration = sessions['duration'].mean()
            # Normaliser (supposant qu'une session de 15 minutes est "idéale")
            duration_score = min(1, avg_duration / 15)
            engagement_factors.append(duration_score)
        
        # Score d'engagement moyen
        engagement_score = sum(engagement_factors) / len(engagement_factors) if engagement_factors else 0
        
        # Score RFE composite
        rfe_score = (
            self.recency_weight * recency_score +
            self.frequency_weight * frequency_score +
            self.engagement_weight * engagement_score
        )
        
        return {
            'recency_score': recency_score,
            'frequency_score': frequency_score,
            'engagement_score': engagement_score,
            'rfe_score': rfe_score
        }
    
    def update_profiles(self, existing_profiles, new_actions):
        """
        Met à jour les profils existants avec de nouvelles actions.
        
        Args:
            existing_profiles (dict): Profils utilisateur existants
            new_actions (list): Nouvelles actions à intégrer
            
        Returns:
            dict: Profils utilisateur mis à jour
        """
        # Convertir les nouvelles actions en DataFrame
        new_actions_df = pd.DataFrame(new_actions)
        if new_actions_df.empty:
            return existing_profiles
            
        new_actions_df['timestamp'] = pd.to_datetime(new_actions_df['timestamp'])
        
        # Date actuelle pour les calculs de récence
        now = datetime.now()
        
        # Mettre à jour chaque profil affecté
        updated_profiles = existing_profiles.copy()
        
        for user_id, user_actions in new_actions_df.groupby('user_id'):
            if user_id in updated_profiles:
                # Récupérer le profil existant
                profile = updated_profiles[user_id]
                
                # Mettre à jour les statistiques de base
                profile['action_count'] += len(user_actions)
                profile['last_action'] = max(
                    user_actions['timestamp'].max().isoformat(),
                    profile.get('last_action', '2000-01-01')
                )
                
                # Mettre à jour les types d'action
                action_types = user_actions['action_type'].value_counts().to_dict()
                for action_type, count in action_types.items():
                    profile['action_types'][action_type] = profile['action_types'].get(action_type, 0) + count
                
                # Mettre à jour les compteurs spécifiques
                profile['job_view_count'] += action_types.get('view_job', 0)
                profile['application_count'] += action_types.get('apply_job', 0)
                
                # Recalculer le taux de conversion
                if profile['job_view_count'] > 0:
                    profile['conversion_rate'] = profile['application_count'] / profile['job_view_count']
                
                # Nous aurions besoin de toutes les actions précédentes pour recalculer correctement les sessions
                # Pour simplifier, nous pouvons approximer
                profile['session_count'] += 1  # Supposer que c'est une nouvelle session
                
                # Mettre à jour les scores RFE
                updated_scores = self._calculate_rfe_scores(user_actions, now)
                profile['recency_score'] = updated_scores['recency_score']  # Basé uniquement sur la dernière action
                profile['frequency_score'] = (profile['frequency_score'] + updated_scores['frequency_score']) / 2
                profile['engagement_score'] = (profile['engagement_score'] + updated_scores['engagement_score']) / 2
                profile['rfe_score'] = (
                    self.recency_weight * profile['recency_score'] +
                    self.frequency_weight * profile['frequency_score'] +
                    self.engagement_weight * profile['engagement_score']
                )
            else:
                # Créer un nouveau profil
                profile = self._build_profile(user_id, user_actions, {}, now)
                updated_profiles[user_id] = profile
                
        return updated_profiles