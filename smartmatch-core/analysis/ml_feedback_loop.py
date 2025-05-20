from typing import Dict, List, Any, Tuple
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import pickle
import sqlite3
import json
import logging
import os
from ..tracking.schema import EventType, FeedbackRating

logger = logging.getLogger(__name__)

class MLFeedbackLoop:
    def __init__(self, ml_optimizer_path: str = 'models/ml_optimizer.pkl', 
                 db_path: str = 'data/tracking.db',
                 min_samples: int = 10):
        self.ml_optimizer_path = ml_optimizer_path
        self.db_path = db_path
        self.min_samples = min_samples
        self.ml_optimizer = None
        
    def load_ml_optimizer(self):
        """Charge le modèle d'optimisation ML existant"""
        try:
            if os.path.exists(self.ml_optimizer_path):
                with open(self.ml_optimizer_path, 'rb') as f:
                    self.ml_optimizer = pickle.load(f)
                logger.info(f"ML Optimizer loaded from {self.ml_optimizer_path}")
                return True
            else:
                logger.warning(f"ML Optimizer file not found at {self.ml_optimizer_path}")
                return False
        except Exception as e:
            logger.error(f"Failed to load ML Optimizer: {str(e)}")
            return False
    
    def save_ml_optimizer(self):
        """Sauvegarde le modèle d'optimisation ML mis à jour"""
        try:
            if self.ml_optimizer:
                with open(self.ml_optimizer_path, 'wb') as f:
                    pickle.dump(self.ml_optimizer, f)
                logger.info(f"ML Optimizer saved to {self.ml_optimizer_path}")
                return True
            else:
                logger.warning("No ML Optimizer model to save")
                return False
        except Exception as e:
            logger.error(f"Failed to save ML Optimizer: {str(e)}")
            return False
    
    def collect_training_data(self, since: datetime = None) -> pd.DataFrame:
        """Collecte et prépare les données pour l'entraînement"""
        if since is None:
            since = datetime.utcnow() - timedelta(days=30)
        since_str = since.isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Récupérer les matchs proposés
            cursor.execute(
                "SELECT match_id, data FROM events WHERE event_type = ? AND timestamp >= ?",
                (EventType.MATCH_PROPOSED.value, since_str)
            )
            proposed_matches = {row[0]: json.loads(row[1]) for row in cursor.fetchall()}
            
            # Récupérer les décisions (accepté/refusé)
            cursor.execute(
                "SELECT match_id, event_type FROM events WHERE "
                "(event_type = ? OR event_type = ?) AND timestamp >= ?",
                (EventType.MATCH_ACCEPTED.value, EventType.MATCH_REJECTED.value, since_str)
            )
            decisions = {row[0]: 1 if row[1] == EventType.MATCH_ACCEPTED.value else 0 
                        for row in cursor.fetchall()}
            
            # Récupérer les feedbacks
            cursor.execute(
                "SELECT match_id, data FROM events WHERE event_type = ? AND timestamp >= ?",
                (EventType.MATCH_FEEDBACK.value, since_str)
            )
            feedbacks = {}
            for row in cursor.fetchall():
                data = json.loads(row[1])
                if 'rating' in data:
                    feedbacks[row[0]] = data['rating']
            
            # Construire le dataframe d'entraînement
            data = []
            for match_id, match_data in proposed_matches.items():
                if 'match_score' in match_data and 'constraint_satisfaction' in match_data:
                    row = {
                        'match_id': match_id,
                        'match_score': match_data['match_score'],
                        'user_decision': decisions.get(match_id, None),
                        'feedback_rating': feedbacks.get(match_id, None),
                    }
                    
                    # Ajouter les valeurs de satisfaction des contraintes
                    for constraint, value in match_data['constraint_satisfaction'].items():
                        row[f'constraint_{constraint}'] = value
                        
                    data.append(row)
            
            return pd.DataFrame(data)
        except Exception as e:
            logger.error(f"Error collecting training data: {str(e)}")
            return pd.DataFrame()
        finally:
            conn.close()
    
    def update_ml_model(self):
        """Met à jour le modèle ML avec les nouvelles données"""
        # Charger le modèle ML existant
        if not self.load_ml_optimizer():
            return False
        
        # Collecter les données d'entraînement
        training_data = self.collect_training_data()
        
        if len(training_data) < self.min_samples:
            logger.info(f"Not enough samples for update: {len(training_data)} < {self.min_samples}")
            return False
            
        # Préparer les données pour l'entraînement
        X, y = self.prepare_training_data(training_data)
        
        if len(X) == 0 or len(y) == 0:
            logger.warning("No valid training data after preparation")
            return False
        
        # Mettre à jour le modèle
        try:
            # Exemple avec un modèle scikit-learn
            self.ml_optimizer.fit(X, y)
            logger.info(f"ML Optimizer updated with {len(X)} samples")
            
            # Sauvegarder le modèle mis à jour
            return self.save_ml_optimizer()
        except Exception as e:
            logger.error(f"Failed to update ML Optimizer: {str(e)}")
            return False
    
    def prepare_training_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prépare les features et labels pour l'entraînement"""
        # Sélectionner les lignes avec au moins une valeur cible
        df = df.dropna(subset=['user_decision', 'feedback_rating'], how='all')
        
        if len(df) == 0:
            return np.array([]), np.array([])
        
        # Extraire les features
        feature_cols = ['match_score'] + [col for col in df.columns if col.startswith('constraint_')]
        X = df[feature_cols].values
        
        # Créer un label combiné (décision, feedback)
        y = []
        for _, row in df.iterrows():
            # Prioriser le feedback s'il est disponible
            if pd.notna(row['feedback_rating']):
                label = (row['feedback_rating'] - 1) / 4  # Normaliser entre 0 et 1
            # Sinon utiliser la décision
            elif pd.notna(row['user_decision']):
                label = row['user_decision']
            else:
                # Ne devrait pas arriver grâce au dropna ci-dessus
                continue
            
            y.append(label)
        
        return np.array(X), np.array(y)