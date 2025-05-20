"""
Module de scoring de préférences pour la Session 8
"""

import os
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from sqlalchemy import create_engine, text
from collections import defaultdict

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PreferenceScorer:
    """Classe pour calculer et gérer des scores de préférence utilisateur."""
    
    def __init__(self, db_url=None):
        """
        Initialise le calculateur de préférences.
        
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
            
        # Paramètres de scoring
        self.decay_factor = 0.8  # Facteur de décroissance pour les événements plus anciens
        self.confidence_threshold = 0.7  # Seuil de confiance minimum
        self.min_sample_size = 5  # Taille d'échantillon minimum pour un score fiable
    
    def get_user_events(self, user_id=None, start_date=None, end_date=None):
        """
        Récupère les événements utilisateur pour le calcul des préférences.
        
        Args:
            user_id (int, optional): ID utilisateur pour filtrer les données.
            start_date (datetime, optional): Date de début pour filtrer les données.
            end_date (datetime, optional): Date de fin pour filtrer les données.
            
        Returns:
            pandas.DataFrame: Événements utilisateur.
        """
        try:
            if self.engine is None:
                # Mode démo: retourner des données simulées
                return self._get_demo_events(user_id)
                
            # Construction de la requête
            query = """
            SELECT 
                t.user_id,
                t.event_type,
                t.event_data,
                t.timestamp
            FROM 
                tracking_events t
            WHERE 1=1
            """
            
            params = {}
            
            # Ajouter les filtres si spécifiés
            if user_id:
                query += " AND t.user_id = :user_id"
                params['user_id'] = user_id
                
            if start_date:
                query += " AND t.timestamp >= :start_date"
                params['start_date'] = start_date
                
            if end_date:
                query += " AND t.timestamp <= :end_date"
                params['end_date'] = end_date
                
            query += " ORDER BY t.user_id, t.timestamp"
            
            # Exécuter la requête
            df = pd.read_sql(query, self.engine, params=params)
            
            # Extraction des données JSON
            if not df.empty and 'event_data' in df.columns:
                try:
                    df['event_data_parsed'] = df['event_data'].apply(lambda x: json.loads(x) if isinstance(x, str) else x)
                    
                    # Extraire les clés communes
                    if len(df) > 0:
                        keys = set()
                        for data in df['event_data_parsed']:
                            if isinstance(data, dict):
                                keys.update(data.keys())
                        
                        for key in keys:
                            df[f'event_{key}'] = df['event_data_parsed'].apply(
                                lambda x: x.get(key) if isinstance(x, dict) else None
                            )
                except Exception as e:
                    logger.warning(f"Erreur lors du parsing des données JSON: {e}")
            
            return df
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des événements utilisateur: {e}")
            # En cas d'erreur, retourner des données simulées
            return self._get_demo_events(user_id)
    
    def _get_demo_events(self, user_id=None):
        """
        Crée des événements simulés pour la démo.
        
        Args:
            user_id (int, optional): ID utilisateur pour filtrer les données.
            
        Returns:
            pandas.DataFrame: Événements simulés.
        """
        # Créer une liste d'utilisateurs
        users = [1, 1, 1, 2, 2, 3, 3]
        
        # Si un user_id est spécifié, ne garder que cet utilisateur
        if user_id is not None:
            users = [user_id] * 5
            
        # Créer des types d'événements
        event_types = ['view', 'like', 'message', 'view', 'share', 'view', 'profile_view']
        
        # Créer des timestamps
        now = datetime.now()
        timestamps = [
            now - timedelta(days=1, hours=2),
            now - timedelta(days=2, hours=1),
            now - timedelta(days=3, minutes=45),
            now - timedelta(days=4, hours=3),
            now - timedelta(days=5, minutes=15),
            now - timedelta(days=6, hours=4),
            now - timedelta(days=7, minutes=30)
        ]
        
        # Créer des données d'événement
        event_data = [
            {'content_id': 101, 'content_type': 'profile', 'duration': 45},
            {'content_id': 101, 'content_type': 'profile', 'preference': 0.8},
            {'content_id': 101, 'content_type': 'message', 'length': 120},
            {'content_id': 202, 'content_type': 'profile', 'duration': 60},
            {'content_id': 202, 'content_type': 'share', 'destination': 'social'},
            {'content_id': 303, 'content_type': 'profile', 'duration': 30},
            {'content_id': 404, 'content_type': 'profile', 'duration': 90}
        ]
        
        # Créer le DataFrame
        df = pd.DataFrame({
            'user_id': users,
            'event_type': event_types,
            'event_data': [json.dumps(data) for data in event_data],
            'timestamp': timestamps,
            'event_data_parsed': event_data
        })
        
        # Extraire les données JSON en colonnes
        for key in ['content_id', 'content_type', 'duration', 'preference', 'length', 'destination']:
            df[f'event_{key}'] = df['event_data_parsed'].apply(
                lambda x: x.get(key) if isinstance(x, dict) else None
            )
            
        return df
    
    def calculate_category_scores(self, events_df, category_field, item_field):
        """
        Calcule les scores pour une combinaison catégorie/élément.
        
        Args:
            events_df (pandas.DataFrame): DataFrame des événements.
            category_field (str): Nom du champ contenant la catégorie.
            item_field (str): Nom du champ contenant l'élément.
            
        Returns:
            dict: Scores par utilisateur/catégorie/élément.
        """
        if events_df.empty or category_field not in events_df.columns or item_field not in events_df.columns:
            return {}
            
        # Grouper par utilisateur
        user_scores = {}
        
        for user_id, user_group in events_df.groupby('user_id'):
            if user_id not in user_scores:
                user_scores[user_id] = {}
                
            # Extraire les catégories et éléments uniques
            categories = user_group[category_field].dropna().unique()
            
            # Pour chaque catégorie
            for category in categories:
                if category not in user_scores[user_id]:
                    user_scores[user_id][category] = {}
                
                # Filtrer les événements pour cette catégorie
                category_events = user_group[user_group[category_field] == category]
                
                # Compter les éléments uniques
                items = category_events[item_field].dropna().unique()
                
                item_counts = {}
                item_timestamps = {}
                
                # Compter les occurrences et stocker les timestamps
                for _, row in category_events.iterrows():
                    item = row[item_field]
                    if pd.isna(item):
                        continue
                        
                    if item not in item_counts:
                        item_counts[item] = 0
                        item_timestamps[item] = []
                        
                    item_counts[item] += 1
                    
                    if 'timestamp' in row and not pd.isna(row['timestamp']):
                        item_timestamps[item].append(row['timestamp'])
                
                # Calculer les scores avec pondération temporelle
                now = datetime.now()
                total_weighted_count = 0
                
                for item, count in item_counts.items():
                    # Initialiser le score
                    if item not in user_scores[user_id][category]:
                        user_scores[user_id][category][item] = {
                            'count': 0,
                            'weighted_count': 0,
                            'timestamps': []
                        }
                    
                    # Appliquer la pondération temporelle
                    weighted_count = 0
                    
                    if item in item_timestamps and item_timestamps[item]:
                        for ts in item_timestamps[item]:
                            # Calculer l'âge en jours
                            age_days = (now - ts).total_seconds() / (24 * 3600)
                            # Appliquer un facteur de décroissance exponentielle
                            weight = self.decay_factor ** (age_days / 30)  # Demi-vie d'un mois
                            weighted_count += weight
                    else:
                        weighted_count = count
                    
                    # Mettre à jour les statistiques
                    user_scores[user_id][category][item]['count'] = count
                    user_scores[user_id][category][item]['weighted_count'] = weighted_count
                    user_scores[user_id][category][item]['timestamps'] = item_timestamps.get(item, [])
                    
                    total_weighted_count += weighted_count
                
                # Normaliser les scores
                if total_weighted_count > 0:
                    for item in user_scores[user_id][category]:
                        score = user_scores[user_id][category][item]['weighted_count'] / total_weighted_count
                        count = user_scores[user_id][category][item]['count']
                        
                        # Calculer la confiance basée sur le nombre d'observations
                        confidence = min(1.0, count / self.min_sample_size)
                        
                        user_scores[user_id][category][item]['score'] = score
                        user_scores[user_id][category][item]['confidence'] = confidence
        
        return user_scores
    
    def save_preference_scores(self, scores):
        """
        Sauvegarde les scores de préférence dans la base de données.
        
        Args:
            scores (dict): Scores par utilisateur/catégorie/élément.
            
        Returns:
            bool: True si succès, False sinon.
        """
        if not scores:
            return False
            
        try:
            if self.engine is None:
                # Mode démo: simuler la sauvegarde
                logger.info(f"Simulation: Scores sauvegardés pour {len(scores)} utilisateurs")
                return True
                
            for user_id, categories in scores.items():
                for category, items in categories.items():
                    for item, data in items.items():
                        if 'score' not in data or 'confidence' not in data:
                            continue
                            
                        # Vérifier si le score existe déjà
                        query = """
                        SELECT user_id FROM preference_scores 
                        WHERE user_id = :user_id AND category = :category AND item = :item
                        """
                        
                        with self.engine.connect() as conn:
                            result = conn.execute(text(query), {
                                'user_id': user_id,
                                'category': category,
                                'item': item
                            })
                            existing = result.fetchone()
                            
                            if existing:
                                # Mettre à jour
                                update_query = """
                                UPDATE preference_scores
                                SET score = :score,
                                    confidence = :confidence,
                                    sample_size = :sample_size,
                                    updated_at = CURRENT_TIMESTAMP
                                WHERE user_id = :user_id AND category = :category AND item = :item
                                """
                                
                                conn.execute(text(update_query), {
                                    'user_id': user_id,
                                    'category': category,
                                    'item': item,
                                    'score': data['score'],
                                    'confidence': data['confidence'],
                                    'sample_size': data['count']
                                })
                            else:
                                # Insérer
                                insert_query = """
                                INSERT INTO preference_scores (
                                    user_id, category, item, score, confidence, sample_size
                                ) VALUES (
                                    :user_id, :category, :item, :score, :confidence, :sample_size
                                )
                                """
                                
                                conn.execute(text(insert_query), {
                                    'user_id': user_id,
                                    'category': category,
                                    'item': item,
                                    'score': data['score'],
                                    'confidence': data['confidence'],
                                    'sample_size': data['count']
                                })
            
            logger.info(f"Scores de préférence sauvegardés pour {len(scores)} utilisateurs")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des scores de préférence: {e}")
            return False
    
    def get_user_preference_scores(self, user_id):
        """
        Récupère les scores de préférence pour un utilisateur.
        
        Args:
            user_id (int): ID de l'utilisateur.
            
        Returns:
            dict: Scores de préférence.
        """
        try:
            if self.engine is None:
                # Mode démo: retourner des scores simulés
                return self._get_demo_preference_scores(user_id)
                
            query = """
            SELECT 
                category, item, score, confidence, sample_size
            FROM 
                preference_scores
            WHERE 
                user_id = :user_id
            ORDER BY 
                category, score DESC
            """
            
            df = pd.read_sql(query, self.engine, params={'user_id': user_id})
            
            if df.empty:
                return {}
                
            # Organiser les scores
            scores = {}
            
            for _, row in df.iterrows():
                category = row['category']
                item = row['item']
                
                if category not in scores:
                    scores[category] = {}
                
                scores[category][item] = {
                    'score': float(row['score']),
                    'confidence': float(row['confidence'])
                }
                
            return scores
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des scores de préférence: {e}")
            # En cas d'erreur, retourner des scores simulés
            return self._get_demo_preference_scores(user_id)
    
    def _get_demo_preference_scores(self, user_id):
        """
        Crée des scores de préférence simulés pour la démo.
        
        Args:
            user_id (int): ID de l'utilisateur.
            
        Returns:
            dict: Scores de préférence simulés.
        """
        # Créer des scores différents selon l'utilisateur
        if user_id == 1:
            return {
                'content_type': {
                    'profile': {'score': 0.65, 'confidence': 0.8},
                    'message': {'score': 0.35, 'confidence': 0.6}
                },
                'action_type': {
                    'view': {'score': 0.5, 'confidence': 0.9},
                    'like': {'score': 0.3, 'confidence': 0.7},
                    'message': {'score': 0.2, 'confidence': 0.6}
                }
            }
        elif user_id == 2:
            return {
                'content_type': {
                    'message': {'score': 0.7, 'confidence': 0.8},
                    'profile': {'score': 0.3, 'confidence': 0.6}
                },
                'action_type': {
                    'message': {'score': 0.6, 'confidence': 0.9},
                    'view': {'score': 0.3, 'confidence': 0.8},
                    'like': {'score': 0.1, 'confidence': 0.5}
                }
            }
        elif user_id == 3:
            return {
                'content_type': {
                    'profile': {'score': 0.9, 'confidence': 0.7},
                    'message': {'score': 0.1, 'confidence': 0.4}
                },
                'action_type': {
                    'view': {'score': 0.8, 'confidence': 0.8},
                    'like': {'score': 0.15, 'confidence': 0.6},
                    'message': {'score': 0.05, 'confidence': 0.3}
                }
            }
        else:
            # Utilisateur par défaut
            return {
                'content_type': {
                    'profile': {'score': 0.5, 'confidence': 0.5},
                    'message': {'score': 0.5, 'confidence': 0.5}
                }
            }
    
    def generate_recommendations(self, user_id):
        """
        Génère des recommandations basées sur les préférences d'un utilisateur.
        
        Args:
            user_id (int): ID de l'utilisateur.
            
        Returns:
            list: Recommandations générées.
        """
        # Récupérer les scores de préférence
        preferences = self.get_user_preference_scores(user_id)
        
        if not preferences:
            return []
            
        recommendations = []
        
        # Générer des recommandations basées sur les types de contenu
        if 'content_type' in preferences:
            content_prefs = preferences['content_type']
            
            # Trier par score
            sorted_content = sorted(
                [(item, data) for item, data in content_prefs.items()],
                key=lambda x: x[1]['score'],
                reverse=True
            )
            
            # Générer des recommandations pour les préférences ayant une confiance suffisante
            for content_type, data in sorted_content:
                if data['confidence'] >= self.confidence_threshold:
                    recommendations.append({
                        'type': 'content',
                        'item': content_type,
                        'score': data['score'],
                        'message': f"Recommandé en fonction de votre préférence pour le contenu de type '{content_type}'"
                    })
        
        # Générer des recommandations basées sur les types d'action
        if 'action_type' in preferences:
            action_prefs = preferences['action_type']
            
            # Trier par score
            sorted_actions = sorted(
                [(item, data) for item, data in action_prefs.items()],
                key=lambda x: x[1]['score'],
                reverse=True
            )
            
            # Générer des recommandations pour les préférences ayant une confiance suffisante
            for action_type, data in sorted_actions:
                if data['confidence'] >= self.confidence_threshold:
                    recommendations.append({
                        'type': 'action',
                        'item': action_type,
                        'score': data['score'],
                        'message': f"Recommandé en fonction de votre préférence pour l'action '{action_type}'"
                    })
        
        return recommendations
    
    def calculate_user_preferences(self, user_id=None, lookback_days=90):
        """
        Calcule les préférences utilisateur.
        
        Args:
            user_id (int, optional): ID utilisateur. Si None, calcule pour tous les utilisateurs.
            lookback_days (int, optional): Nombre de jours à considérer.
            
        Returns:
            dict: Résultats du calcul.
        """
        try:
            # Définir la période de lookback
            start_date = datetime.now() - timedelta(days=lookback_days)
            
            # Récupérer les événements
            events = self.get_user_events(
                user_id=user_id,
                start_date=start_date
            )
            
            if events.empty:
                return {
                    'status': 'warning',
                    'message': 'Aucun événement disponible',
                    'users_analyzed': 0
                }
                
            # Liste des catégories et éléments à analyser
            category_item_pairs = [
                ('event_content_type', 'event_content_type'),  # Préférences de type de contenu
                ('event_type', 'event_type')  # Préférences de type d'action
            ]
            
            all_scores = {}
            valid_categories = []
            
            # Pour chaque paire catégorie/élément
            for category_field, item_field in category_item_pairs:
                if category_field in events.columns and item_field in events.columns:
                    # Calculer les scores
                    scores = self.calculate_category_scores(events, category_field, item_field)
                    
                    # Fusionner avec les scores existants
                    for user_id, user_scores in scores.items():
                        if user_id not in all_scores:
                            all_scores[user_id] = {}
                            
                        for category, category_scores in user_scores.items():
                            # Simplifier le nom de la catégorie
                            simple_category = category_field.replace('event_', '')
                            all_scores[user_id][simple_category] = category_scores
                            
                            if simple_category not in valid_categories:
                                valid_categories.append(simple_category)
            
            # Sauvegarder les scores
            save_success = self.save_preference_scores(all_scores)
            
            return {
                'status': 'success' if save_success else 'partial',
                'message': 'Calcul des préférences terminé',
                'users_analyzed': len(all_scores),
                'categories_computed': valid_categories,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Erreur lors du calcul des préférences: {e}")
            return {
                'status': 'error',
                'message': f"Erreur lors du calcul: {str(e)}",
                'users_analyzed': 0
            }
