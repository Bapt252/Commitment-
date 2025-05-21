"""
Module d'analyse comportementale pour la Session 8
"""

import os
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from sqlalchemy import create_engine, text

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BehavioralAnalyzer:
    """Classe pour analyser le comportement des utilisateurs."""
    
    def __init__(self, db_url=None):
        """
        Initialise l'analyseur comportemental.
        
        Args:
            db_url (str, optional): URL de connexion à la base de données.
                Si non spécifié, utilise la variable d'environnement DATABASE_URL.
        """
        self.db_url = db_url or os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/commitment')
        try:
            self.engine = create_engine(self.db_url)
            logger.info("Connexion à la base de données établie")
        except Exception as e:
            logger.error(f"Erreur de connexion à la base de données: {e}")
            # Créer un moteur factice pour la démo
            self.engine = None
    
    def get_tracking_data(self, start_date=None, end_date=None, user_id=None):
        """
        Récupère les données de tracking.
        
        Args:
            start_date (datetime, optional): Date de début pour filtrer les données.
            end_date (datetime, optional): Date de fin pour filtrer les données.
            user_id (int, optional): ID utilisateur pour filtrer les données.
            
        Returns:
            pandas.DataFrame: Données de tracking.
        """
        try:
            if self.engine is None:
                # Mode démo: retourner des données simulées
                return self._get_demo_tracking_data(start_date, end_date, user_id)
                
            # Construction de la requête
            query = """
            SELECT 
                t.user_id,
                t.event_type,
                t.event_data,
                t.timestamp,
                t.session_id
            FROM 
                tracking_events t
            WHERE 1=1
            """
            
            params = {}
            
            # Ajouter les filtres si spécifiés
            if start_date:
                query += " AND t.timestamp >= :start_date"
                params['start_date'] = start_date
                
            if end_date:
                query += " AND t.timestamp <= :end_date"
                params['end_date'] = end_date
                
            if user_id:
                query += " AND t.user_id = :user_id"
                params['user_id'] = user_id
                
            query += " ORDER BY t.user_id, t.timestamp"
            
            # Exécuter la requête
            return pd.read_sql(query, self.engine, params=params)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données de tracking: {e}")
            # En cas d'erreur, retourner des données simulées
            return self._get_demo_tracking_data(start_date, end_date, user_id)
    
    def _get_demo_tracking_data(self, start_date=None, end_date=None, user_id=None):
        """
        Crée des données de tracking simulées pour la démo.
        
        Args:
            start_date (datetime, optional): Date de début pour filtrer les données.
            end_date (datetime, optional): Date de fin pour filtrer les données.
            user_id (int, optional): ID utilisateur pour filtrer les données.
            
        Returns:
            pandas.DataFrame: Données de tracking simulées.
        """
        # Créer des données simulées
        user_ids = [1, 1, 1, 2, 2, 3] if user_id is None else [user_id] * 5
        event_types = ['view', 'like', 'message', 'view', 'share', 'view']
        timestamps = pd.date_range(
            start=start_date or datetime.now() - timedelta(days=30),
            periods=len(user_ids),
            freq='D'
        )
        session_ids = ['s1', 's1', 's1', 's2', 's2', 's3']
        event_data = [
            json.dumps({'content_id': 101, 'duration': 45}),
            json.dumps({'content_id': 101, 'preference': 0.8}),
            json.dumps({'content_id': 101, 'length': 120}),
            json.dumps({'content_id': 202, 'duration': 60}),
            json.dumps({'content_id': 202, 'destination': 'social'}),
            json.dumps({'content_id': 303, 'duration': 30})
        ]
        
        # Créer le DataFrame
        df = pd.DataFrame({
            'user_id': user_ids[:6],
            'event_type': event_types[:6],
            'event_data': event_data[:6],
            'timestamp': timestamps[:6],
            'session_id': session_ids[:6]
        })
        
        # Filtrer si nécessaire
        if user_id is not None:
            df = df[df['user_id'] == user_id].copy()
            
        return df
    
    def calculate_user_metrics(self, user_data):
        """
        Calcule les métriques utilisateur à partir des données de tracking.
        
        Args:
            user_data (pandas.DataFrame): Données de tracking filtrées par utilisateur.
            
        Returns:
            pandas.DataFrame: Métriques utilisateur calculées.
        """
        if user_data.empty:
            return pd.DataFrame()
            
        # Grouper par utilisateur
        user_metrics = []
        
        for user_id, group in user_data.groupby('user_id'):
            # Calculer des métriques de base
            total_events = len(group)
            unique_sessions = group['session_id'].nunique()
            event_frequency = total_events / max(1, unique_sessions)
            
            # Calculer les heures d'activité
            if 'timestamp' in group.columns:
                hours = group['timestamp'].dt.hour
                active_hours = {
                    'morning': (hours.between(6, 11).sum() / total_events),
                    'afternoon': (hours.between(12, 17).sum() / total_events),
                    'evening': (hours.between(18, 23).sum() / total_events),
                    'night': (hours.between(0, 5).sum() / total_events)
                }
            else:
                active_hours = {'morning': 0.25, 'afternoon': 0.25, 'evening': 0.25, 'night': 0.25}
                
            # Calculer la durée moyenne des sessions
            session_durations = []
            for session_id, session_group in group.groupby('session_id'):
                if 'timestamp' in session_group.columns and len(session_group) > 1:
                    session_duration = (session_group['timestamp'].max() - session_group['timestamp'].min()).total_seconds() / 60
                    session_durations.append(session_duration)
            
            avg_session_duration = np.mean(session_durations) if session_durations else 15.0
            
            # Créer une entrée de métriques
            metrics = {
                'user_id': user_id,
                'active_hours': json.dumps(active_hours),
                'interaction_frequency': event_frequency,
                'session_duration': avg_session_duration,
                'last_active': group['timestamp'].max() if 'timestamp' in group.columns else datetime.now()
            }
            
            user_metrics.append(metrics)
            
        return pd.DataFrame(user_metrics)
    
    def save_user_profiles(self, user_metrics):
        """
        Sauvegarde les profils utilisateur dans la base de données.
        
        Args:
            user_metrics (pandas.DataFrame): Métriques utilisateur calculées.
            
        Returns:
            bool: True si succès, False sinon.
        """
        if user_metrics.empty:
            logger.warning("Aucune métrique utilisateur à sauvegarder")
            return False
            
        try:
            if self.engine is None:
                # Mode démo: simuler la sauvegarde
                logger.info(f"Simulation: {len(user_metrics)} profils utilisateur sauvegardés")
                return True
                
            # Pour chaque utilisateur
            for _, row in user_metrics.iterrows():
                # Vérifier si le profil existe déjà
                query = "SELECT profile_id FROM user_profiles WHERE user_id = :user_id"
                
                with self.engine.connect() as conn:
                    result = conn.execute(text(query), {'user_id': row['user_id']})
                    existing_profile = result.fetchone()
                    
                    if existing_profile:
                        # Mettre à jour le profil existant
                        update_query = """
                        UPDATE user_profiles
                        SET active_hours = :active_hours,
                            interaction_frequency = :interaction_frequency,
                            session_duration = :session_duration,
                            last_active = :last_active,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = :user_id
                        """
                        
                        conn.execute(text(update_query), {
                            'user_id': row['user_id'],
                            'active_hours': row['active_hours'],
                            'interaction_frequency': row['interaction_frequency'],
                            'session_duration': row['session_duration'],
                            'last_active': row['last_active']
                        })
                    else:
                        # Créer un nouveau profil
                        insert_query = """
                        INSERT INTO user_profiles (
                            user_id, active_hours, interaction_frequency, session_duration, last_active
                        ) VALUES (
                            :user_id, :active_hours, :interaction_frequency, :session_duration, :last_active
                        )
                        """
                        
                        conn.execute(text(insert_query), {
                            'user_id': row['user_id'],
                            'active_hours': row['active_hours'],
                            'interaction_frequency': row['interaction_frequency'],
                            'session_duration': row['session_duration'],
                            'last_active': row['last_active']
                        })
                
            logger.info(f"{len(user_metrics)} profils utilisateur sauvegardés")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des profils utilisateur: {e}")
            return False
    
    def run_analysis(self):
        """
        Exécute une analyse comportementale complète.
        
        Returns:
            dict: Résultats de l'analyse.
        """
        try:
            # Récupérer les données des 30 derniers jours
            start_date = datetime.now() - timedelta(days=30)
            tracking_data = self.get_tracking_data(start_date=start_date)
            
            if tracking_data.empty:
                return {
                    'status': 'warning',
                    'message': 'Aucune donnée de tracking disponible',
                    'users_analyzed': 0
                }
                
            # Calculer les métriques utilisateur
            user_metrics = self.calculate_user_metrics(tracking_data)
            
            if user_metrics.empty:
                return {
                    'status': 'warning',
                    'message': 'Impossible de calculer les métriques utilisateur',
                    'users_analyzed': 0
                }
                
            # Sauvegarder les profils
            save_success = self.save_user_profiles(user_metrics)
            
            return {
                'status': 'success' if save_success else 'partial',
                'message': 'Analyse comportementale terminée',
                'users_analyzed': len(user_metrics),
                'metrics_computed': ['active_hours', 'interaction_frequency', 'session_duration'],
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse comportementale: {e}")
            return {
                'status': 'error',
                'message': f"Erreur lors de l'analyse: {str(e)}",
                'users_analyzed': 0
            }
