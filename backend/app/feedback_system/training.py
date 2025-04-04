from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import mlflow
import os
import joblib
import json
import requests
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

from app.feedback_system.crud import (
    get_recent_feedbacks,
    create_model_metrics,
    get_deployed_model_metrics,
    deploy_model,
    create_feedback_alert
)
from app.feedback_system.schemas import ModelMetricsCreate, FeedbackAlertCreate

# Configurer le logging
logger = logging.getLogger(__name__)

# Configuration MLflow
MLFLOW_TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000")
MLFLOW_EXPERIMENT_NAME = os.environ.get("MLFLOW_EXPERIMENT_NAME", "commitment_matching_model")
MODELS_PATH = os.path.join(os.path.dirname(__file__), '../../../ml_engine/models/')

# Configuration Slack (pour notifications)
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "")


def check_threshold_for_retraining(db: Session) -> bool:
    """Vérifie si le seuil de feedback est atteint pour déclencher un réentraînement"""
    # Récupérer les feedbacks récents
    recent_feedbacks = get_recent_feedbacks(db, days=7)
    
    # Récupérer la date du dernier entraînement
    last_metrics = get_deployed_model_metrics(db, "matching")
    
    last_training_date = last_metrics.training_date if last_metrics else datetime.min
    new_feedback_count = len([f for f in recent_feedbacks if f.feedback_date > last_training_date])
    
    # Vérifier si le seuil est atteint
    threshold = 50  # Ajustable selon vos besoins
    if new_feedback_count >= threshold:
        logger.info(f"Seuil de {threshold} nouveaux feedbacks atteint. Déclenchement du réentraînement.")
        # Lancer le réentraînement
        trigger_training_pipeline(db)
        return True
    
    return False


def trigger_training_pipeline(db: Session) -> bool:
    """Déclenche le pipeline d'entraînement du modèle de matching"""
    try:
        # Configurer MLflow
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)
        
        # Collecter les données pour l'entraînement
        training_data = collect_training_data(db)
        
        if len(training_data) < 100:  # Vérifier qu'il y a assez de données
            logger.warning("Pas assez de données pour réentraîner le modèle.")
            return False
        
        model_version = f"matching_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        with mlflow.start_run(run_name=model_version):
            # Préparation des données
            X, y = preprocess_data(training_data)
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Logging des métadonnées
            mlflow.log_param("data_size", len(training_data))
            mlflow.log_param("training_date", datetime.now().isoformat())
            
            # Entraînement du modèle
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            
            # Validation croisée
            cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='f1')
            mlflow.log_metric("cv_f1_mean", cv_scores.mean())
            
            # Entraînement final
            model.fit(X_train, y_train)
            
            # Évaluation
            y_pred = model.predict(X_test)
            y_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else None
            
            acc = accuracy_score(y_test, y_pred)
            prec = precision_score(y_test, y_pred, zero_division=0)
            rec = recall_score(y_test, y_pred, zero_division=0)
            f1 = f1_score(y_test, y_pred, zero_division=0)
            auc = roc_auc_score(y_test, y_proba) if y_proba is not None else None
            
            # Logging des métriques
            mlflow.log_metric("accuracy", acc)
            mlflow.log_metric("precision", prec)
            mlflow.log_metric("recall", rec)
            mlflow.log_metric("f1_score", f1)
            if auc is not None:
                mlflow.log_metric("auc_roc", auc)
            
            # Sauvegarde du modèle avec MLflow
            mlflow.sklearn.log_model(model, model_version)
            
            # Sauvegarde locale du modèle
            os.makedirs(MODELS_PATH, exist_ok=True)
            joblib.dump(model, os.path.join(MODELS_PATH, f"{model_version}.joblib"))
            
            # Calculer les métriques business
            avg_satisfaction = calculate_avg_satisfaction(db)
            conversion_rate = calculate_conversion_rate(db)
            
            # Créer les métriques en BDD
            metrics = ModelMetricsCreate(
                model_version=model_version,
                model_type="matching",
                accuracy=acc,
                precision=prec,
                recall=rec,
                f1_score=f1,
                auc_roc=auc,
                avg_satisfaction=avg_satisfaction,
                conversion_rate=conversion_rate,
                dataset_size=len(training_data),
                is_deployed=False,  # Sera déployé après évaluation
                model_config=json.dumps(model.get_params())
            )
            
            db_metrics = create_model_metrics(db, metrics)
            
            # Décider si le modèle doit être déployé
            should_deploy = evaluate_deployment_decision(db, f1, auc)
            
            if should_deploy:
                deploy_model(db, model_version, "matching")
                send_deployment_notification(model_version, {
                    "accuracy": acc,
                    "f1_score": f1,
                    "improvement": "X% par rapport au modèle précédent"  # À calculer réellement
                })
            
            return True
            
    except Exception as e:
        logger.error(f"Erreur lors du réentraînement du modèle: {str(e)}")
        # Créer une alerte pour signaler l'échec
        create_feedback_alert(
            db,
            FeedbackAlertCreate(
                alert_type="training_failure",
                severity="critical",
                message="Échec du réentraînement du modèle",
                details=str(e)
            )
        )
        return False


def collect_training_data(db: Session) -> pd.DataFrame:
    """Collecte les données pour l'entraînement à partir de la base"""
    # Dans une implémentation réelle, vous récupéreriez les données de votre base
    # et les transformeriez en DataFrame pour l'entraînement
    
    # Exemple simplifié (à remplacer par vos vraies requêtes SQL):
    # 1. Récupérer tous les matchings avec leurs feedbacks
    # 2. Extraire les features pertinentes
    
    # Simulation avec des données fictives
    data = [
        {"matching_score": 0.85, "skills_match": 0.9, "exp_match": 0.8, "successful": 1},
        {"matching_score": 0.75, "skills_match": 0.8, "exp_match": 0.7, "successful": 1},
        {"matching_score": 0.65, "skills_match": 0.7, "exp_match": 0.6, "successful": 0},
        # ... plus de données
    ]
    
    return pd.DataFrame(data)


def preprocess_data(data: pd.DataFrame) -> tuple:
    """Prétraite les données pour l'entraînement"""
    # Simulation simple
    X = data.drop("successful", axis=1)
    y = data["successful"]
    
    return X, y


def evaluate_deployment_decision(db: Session, f1_new: float, auc_new: Optional[float]) -> bool:
    """Décide si le nouveau modèle doit être déployé en se basant sur ses performances"""
    # Récupérer le modèle actuellement déployé
    current_model = get_deployed_model_metrics(db, "matching")
    
    if not current_model:
        # Aucun modèle déployé, donc on déploie celui-ci
        return True
    
    # Calculer un score combiné pour la comparaison
    # On pourrait ajuster les poids selon l'importance relative des métriques
    new_combined = 0.7 * f1_new + 0.3 * (auc_new or 0)
    current_combined = 0.7 * (current_model.f1_score or 0) + 0.3 * (current_model.auc_roc or 0)
    
    # Exiger une amélioration minimale (ex: 1%)
    improvement_threshold = 0.01
    
    return new_combined > current_combined * (1 + improvement_threshold)


def calculate_avg_satisfaction(db: Session, days: int = 30) -> float:
    """Calcule la satisfaction moyenne basée sur les feedbacks récents"""
    recent_feedbacks = get_recent_feedbacks(db, days)
    
    if not recent_feedbacks:
        return 0.0
    
    # Normaliser les ratings de 1-5 à 0-1
    return sum((f.rating - 1) / 4 for f in recent_feedbacks) / len(recent_feedbacks)


def calculate_conversion_rate(db: Session, days: int = 30) -> float:
    """Calcule le taux de conversion (matchings qui ont conduit à une interaction)"""
    recent_feedbacks = get_recent_feedbacks(db, days)
    
    if not recent_feedbacks:
        return 0.0
    
    interacted = sum(1 for f in recent_feedbacks if f.interaction_happened)
    return interacted / len(recent_feedbacks)


def send_deployment_notification(model_version: str, metrics: Dict[str, Any]) -> bool:
    """Envoie une notification de déploiement d'un nouveau modèle"""
    if not SLACK_WEBHOOK_URL:
        logger.info(f"Nouveau modèle déployé: {model_version} avec métriques: {metrics}")
        return False
    
    message = {
        "text": f":rocket: Nouveau modèle déployé: {model_version}",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": ":rocket: Nouveau modèle déployé!"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Version:* {model_version}\n*Date:* {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Métriques:*\n• Accuracy: {metrics['accuracy']:.2f}\n• F1 Score: {metrics['f1_score']:.2f}\n• Amélioration: {metrics['improvement']}"
                }
            }
        ]
    }
    
    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=message)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de la notification: {str(e)}")
        return False
