"""
Module de prédiction de satisfaction utilisateur.
Utilise des modèles d'apprentissage automatique pour prédire la satisfaction des utilisateurs.
"""

import logging
import json
import pickle
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional, Union
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

from feedback_service.models import (
    Feedback, UserSatisfactionModel, ModelTrainingLog,
    Sentiment, FeedbackType, FeedbackChannel
)

# Configuration du logger
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Constantes
MODEL_VERSION = "1.0.0"
SATISFACTION_THRESHOLD = 3.5  # Sur une échelle de 1 à 5
CONFIDENCE_THRESHOLD = 0.7    # Confiance minimale


class SatisfactionPredictor:
    """Classe pour prédire la satisfaction des utilisateurs."""
    
    def __init__(self, db_session: Session):
        """
        Initialise le prédicteur de satisfaction.
        
        Args:
            db_session: Session de base de données SQLAlchemy
        """
        self.db_session = db_session
        self.model = None
        self.scaler = None
        self.feature_names = None
    
    def train_model(self, min_samples: int = 50) -> Dict[str, Any]:
        """
        Entraîne le modèle de prédiction de satisfaction.
        
        Args:
            min_samples: Nombre minimum d'échantillons pour l'entraînement
            
        Returns:
            Résultats de l'entraînement avec les métriques
        """
        # Récupérer les données d'entraînement
        training_data = self._prepare_training_data()
        
        if len(training_data) < min_samples:
            logger.warning(f"Pas assez de données pour entraîner le modèle: {len(training_data)} < {min_samples}")
            return {
                "success": False,
                "reason": "insufficient_data",
                "samples": len(training_data),
                "min_samples": min_samples
            }
        
        # Convertir en DataFrame et préparer les features
        df = pd.DataFrame(training_data)
        
        # Définir les features et la target
        X = df.drop(columns=['user_id', 'target_satisfaction'])
        y = df['target_satisfaction']
        self.feature_names = X.columns.tolist()
        
        # Séparation train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Normalisation des features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Imputation des valeurs manquantes
        imputer = SimpleImputer(strategy='mean')
        X_train_imputed = imputer.fit_transform(X_train_scaled)
        X_test_imputed = imputer.transform(X_test_scaled)
        
        # Entraînement du modèle RandomForest
        start_time = datetime.utcnow()
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_leaf=5,
            random_state=42
        )
        model.fit(X_train_imputed, y_train)
        training_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Évaluation du modèle
        y_pred = model.predict(X_test_imputed)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)
        
        # Sauvegarder le modèle
        self.model = model
        
        # Enregistrer les résultats d'entraînement
        training_log = ModelTrainingLog(
            model_type="satisfaction",
            version=MODEL_VERSION,
            metrics={
                "mse": mse,
                "rmse": rmse,
                "r2": r2,
                "samples": len(df)
            },
            parameters={
                "n_estimators": 100,
                "max_depth": 10,
                "min_samples_leaf": 5,
                "features": self.feature_names
            },
            training_time=training_time
        )
        self.db_session.add(training_log)
        self.db_session.commit()
        
        logger.info(f"Modèle entraîné avec {len(df)} échantillons, RMSE={rmse:.4f}, R²={r2:.4f}")
        
        return {
            "success": True,
            "metrics": {
                "mse": mse,
                "rmse": rmse,
                "r2": r2,
                "samples": len(df)
            },
            "training_time": training_time,
            "model_version": MODEL_VERSION,
            "feature_importance": dict(zip(
                self.feature_names, 
                model.feature_importances_.tolist()
            ))
        }
    
    def predict_satisfaction(self, user_id: int) -> Dict[str, Any]:
        """
        Prédit le niveau de satisfaction d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Prédiction de satisfaction avec le score et les facteurs
        """
        # Vérifier si le modèle est entraîné
        if self.model is None:
            # Charger ou entraîner le modèle
            latest_model = self._load_latest_model()
            if latest_model is None:
                training_result = self.train_model()
                if not training_result.get("success", False):
                    return {
                        "success": False,
                        "reason": "model_not_available",
                        "details": training_result
                    }
        
        # Récupérer les données pour l'utilisateur
        user_data = self._prepare_user_data(user_id)
        
        if not user_data:
            logger.warning(f"Données insuffisantes pour prédire la satisfaction de l'utilisateur {user_id}")
            return {
                "success": False,
                "reason": "insufficient_user_data"
            }
        
        # Préparer les features
        X = pd.DataFrame([user_data])
        X = X.drop(columns=['user_id'])
        
        # Ajouter les colonnes manquantes et réordonner
        for feature in self.feature_names:
            if feature not in X.columns:
                X[feature] = 0
        X = X[self.feature_names]
        
        # Normaliser et imputer
        X_scaled = self.scaler.transform(X)
        imputer = SimpleImputer(strategy='mean')
        X_imputed = imputer.fit_transform(X_scaled)
        
        # Prédire
        satisfaction_score = float(self.model.predict(X_imputed)[0])
        
        # Calculer la confiance (basée sur nombre de feedbacks)
        feedback_count = sum(user_data.get(f"count_{channel.value}", 0) 
                             for channel in FeedbackChannel)
        confidence = min(feedback_count / 10, 1.0)  # Max confiance à 10+ feedbacks
        
        # Identifier les facteurs principaux
        feature_importance = self.model.feature_importances_
        sorted_features = sorted(
            zip(self.feature_names, feature_importance),
            key=lambda x: x[1],
            reverse=True
        )
        top_factors = {feature: float(importance) 
                      for feature, importance in sorted_features[:5]}
        
        # Enregistrer la prédiction
        self._save_prediction(user_id, satisfaction_score, confidence, top_factors)
        
        return {
            "success": True,
            "user_id": user_id,
            "satisfaction_score": satisfaction_score,
            "confidence": confidence,
            "is_satisfied": satisfaction_score >= SATISFACTION_THRESHOLD,
            "top_factors": top_factors,
            "prediction_time": datetime.utcnow().isoformat()
        }
    
    def update_all_predictions(self, min_confidence: float = 0.5) -> Dict[str, Any]:
        """
        Met à jour les prédictions pour tous les utilisateurs.
        
        Args:
            min_confidence: Confiance minimale pour les prédictions
            
        Returns:
            Résultats de la mise à jour
        """
        # Vérifier si le modèle est disponible
        if self.model is None:
            latest_model = self._load_latest_model()
            if latest_model is None:
                training_result = self.train_model()
                if not training_result.get("success", False):
                    return {
                        "success": False,
                        "reason": "model_not_available",
                        "details": training_result
                    }
        
        # Récupérer tous les utilisateurs distincts
        users = self.db_session.query(Feedback.user_id).distinct().all()
        user_ids = [user[0] for user in users]
        
        predictions = []
        for user_id in user_ids:
            prediction = self.predict_satisfaction(user_id)
            if (prediction.get("success", False) and 
                prediction.get("confidence", 0) >= min_confidence):
                predictions.append(prediction)
        
        return {
            "success": True,
            "total_users": len(user_ids),
            "predictions_made": len(predictions),
            "prediction_time": datetime.utcnow().isoformat()
        }
    
    def get_user_satisfaction(self, user_id: int) -> Dict[str, Any]:
        """
        Récupère la satisfaction prédite pour un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Données de satisfaction de l'utilisateur
        """
        # Vérifier si une prédiction existe
        prediction = self.db_session.query(UserSatisfactionModel).filter_by(
            user_id=user_id
        ).first()
        
        if prediction:
            return {
                "success": True,
                "user_id": user_id,
                "satisfaction_score": prediction.satisfaction_score,
                "confidence": prediction.confidence,
                "is_satisfied": prediction.satisfaction_score >= SATISFACTION_THRESHOLD,
                "factors": json.loads(prediction.factors) if isinstance(prediction.factors, str) else prediction.factors,
                "last_updated": prediction.last_updated.isoformat() if prediction.last_updated else None
            }
        else:
            # Faire une prédiction si aucune n'existe
            return self.predict_satisfaction(user_id)
    
    def _prepare_training_data(self) -> List[Dict[str, Any]]:
        """
        Prépare les données d'entraînement pour le modèle.
        
        Returns:
            Liste des échantillons d'entraînement
        """
        # Récupérer tous les feedbacks
        feedbacks = self.db_session.query(Feedback).all()
        
        # Regrouper par utilisateur
        user_feedbacks = {}
        for feedback in feedbacks:
            if feedback.user_id not in user_feedbacks:
                user_feedbacks[feedback.user_id] = []
            user_feedbacks[feedback.user_id].append(feedback)
        
        # Construire les features pour chaque utilisateur
        training_data = []
        for user_id, feedbacks in user_feedbacks.items():
            user_data = self._extract_user_features(user_id, feedbacks)
            
            # Calculer la cible (satisfaction moyenne basée sur les ratings)
            ratings = [f.rating for f in feedbacks if f.rating is not None]
            if ratings:
                user_data["target_satisfaction"] = sum(ratings) / len(ratings)
                training_data.append(user_data)
        
        return training_data
    
    def _prepare_user_data(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Prépare les données d'un utilisateur pour la prédiction.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Dictionnaire des features de l'utilisateur
        """
        # Récupérer les feedbacks de l'utilisateur
        feedbacks = self.db_session.query(Feedback).filter_by(user_id=user_id).all()
        
        if not feedbacks:
            return None
        
        # Extraire les features
        return self._extract_user_features(user_id, feedbacks)
    
    def _extract_user_features(self, user_id: int, feedbacks: List[Feedback]) -> Dict[str, Any]:
        """
        Extrait les features pour un utilisateur à partir de ses feedbacks.
        
        Args:
            user_id: ID de l'utilisateur
            feedbacks: Liste des feedbacks de l'utilisateur
            
        Returns:
            Dictionnaire des features de l'utilisateur
        """
        # Initialiser les features
        features = {
            "user_id": user_id,
            # Compteurs par canal
            "count_rating": 0,
            "count_thumbs": 0,
            "count_comment": 0,
            "count_suggestion": 0,
            "count_survey": 0,
            "count_behavior": 0,
            "count_other": 0,
            # Compteurs par type
            "count_explicit": 0,
            "count_implicit": 0,
            "count_system": 0,
            # Compteurs par sentiment
            "count_positive": 0,
            "count_neutral": 0,
            "count_negative": 0,
            "count_unknown": 0,
            # Moyennes
            "avg_rating": 0,
            # Temporalité
            "days_since_first": 0,
            "days_since_last": 0,
            "feedback_frequency": 0  # Feedbacks par jour
        }
        
        # Compteurs
        for feedback in feedbacks:
            # Par canal
            channel_key = f"count_{feedback.channel.value}"
            features[channel_key] += 1
            
            # Par type
            type_key = f"count_{feedback.feedback_type.value}"
            features[type_key] += 1
            
            # Par sentiment
            sentiment_key = f"count_{feedback.sentiment.value}"
            features[sentiment_key] += 1
        
        # Moyennes
        ratings = [f.rating for f in feedbacks if f.rating is not None]
        if ratings:
            features["avg_rating"] = sum(ratings) / len(ratings)
        
        # Temporalité
        if feedbacks:
            dates = [f.created_at for f in feedbacks]
            first_date = min(dates)
            last_date = max(dates)
            now = datetime.utcnow()
            
            features["days_since_first"] = (now - first_date).days
            features["days_since_last"] = (now - last_date).days
            
            if features["days_since_first"] > 0:
                features["feedback_frequency"] = len(feedbacks) / features["days_since_first"]
        
        return features
    
    def _save_prediction(
        self, user_id: int, satisfaction_score: float, 
        confidence: float, factors: Dict[str, float]
    ) -> None:
        """
        Enregistre une prédiction de satisfaction en base de données.
        
        Args:
            user_id: ID de l'utilisateur
            satisfaction_score: Score de satisfaction prédit
            confidence: Confiance dans la prédiction
            factors: Facteurs influençant la prédiction
        """
        # Vérifier si une prédiction existe déjà
        existing = self.db_session.query(UserSatisfactionModel).filter_by(
            user_id=user_id
        ).first()
        
        if existing:
            # Mettre à jour
            existing.satisfaction_score = satisfaction_score
            existing.confidence = confidence
            existing.factors = factors
            existing.last_updated = datetime.utcnow()
        else:
            # Créer une nouvelle
            model = UserSatisfactionModel(
                user_id=user_id,
                satisfaction_score=satisfaction_score,
                confidence=confidence,
                factors=factors
            )
            self.db_session.add(model)
        
        self.db_session.commit()
    
    def _load_latest_model(self) -> Optional[Any]:
        """
        Charge le dernier modèle entraîné.
        
        Returns:
            Modèle chargé ou None si aucun modèle disponible
        """
        # Pour l'instant, retourne None car nous ne sauvegardons pas encore le modèle sur disque
        # Dans une implémentation réelle, nous chargerions le modèle à partir du disque
        return None
    
    def _save_model(self) -> None:
        """
        Sauvegarde le modèle sur disque.
        """
        # Cette méthode serait implémentée dans une version réelle
        # pour sauvegarder le modèle sur disque
        pass
