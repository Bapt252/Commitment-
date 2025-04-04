from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from app.feedback_system.models import (
    Matching, 
    MatchingFeedback, 
    ModelMetrics, 
    FeedbackAlert
)
from app.feedback_system.schemas import (
    MatchingFeedbackCreate,
    ModelMetricsCreate,
    FeedbackAlertCreate
)


# CRUD pour MatchingFeedback
def create_matching_feedback(db: Session, feedback: MatchingFeedbackCreate) -> MatchingFeedback:
    """Crée un nouveau feedback de matching"""
    db_feedback = MatchingFeedback(
        matching_id=feedback.matching_id,
        user_id=feedback.user_id,
        rating=feedback.rating,
        comment=feedback.comment,
        interaction_happened=feedback.interaction_happened,
        time_to_first_message=feedback.time_to_first_message,
        message_count=feedback.message_count,
        engagement_duration=feedback.engagement_duration
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback


def get_matching_feedback(db: Session, feedback_id: int) -> Optional[MatchingFeedback]:
    """Récupère un feedback par son ID"""
    return db.query(MatchingFeedback).filter(MatchingFeedback.id == feedback_id).first()


def get_matching_feedbacks(db: Session, skip: int = 0, limit: int = 100) -> List[MatchingFeedback]:
    """Récupère tous les feedbacks avec pagination"""
    return db.query(MatchingFeedback).offset(skip).limit(limit).all()


def get_feedbacks_by_matching(db: Session, matching_id: int) -> List[MatchingFeedback]:
    """Récupère tous les feedbacks pour un matching donné"""
    return db.query(MatchingFeedback).filter(MatchingFeedback.matching_id == matching_id).all()


def get_recent_feedbacks(db: Session, days: int = 30) -> List[MatchingFeedback]:
    """Récupère les feedbacks récents"""
    cutoff_date = datetime.now() - timedelta(days=days)
    return db.query(MatchingFeedback).filter(MatchingFeedback.feedback_date >= cutoff_date).all()


def get_feedback_stats(db: Session, days: int = 30) -> Dict[str, Any]:
    """Récupère des statistiques sur les feedbacks"""
    cutoff_date = datetime.now() - timedelta(days=days)
    
    # Récupérer les feedbacks récents
    recent_feedbacks = db.query(MatchingFeedback).filter(
        MatchingFeedback.feedback_date >= cutoff_date
    ).all()
    
    # Calculer les statistiques
    total = len(recent_feedbacks)
    if total == 0:
        return {
            "total_feedbacks": 0,
            "average_rating": 0,
            "rating_distribution": {},
            "recent_trend": {}
        }
    
    # Note moyenne
    avg_rating = sum(f.rating for f in recent_feedbacks) / total
    
    # Distribution des notes
    rating_distribution = {}
    for i in range(1, 6):
        rating_distribution[i] = len([f for f in recent_feedbacks if f.rating == i])
    
    # Tendance récente
    # Diviser la période en 4 segments
    segment_days = days // 4
    recent_trend = {}
    for i in range(4):
        start_date = cutoff_date + timedelta(days=i*segment_days)
        end_date = cutoff_date + timedelta(days=(i+1)*segment_days)
        segment_feedbacks = [f for f in recent_feedbacks 
                             if start_date <= f.feedback_date < end_date]
        if segment_feedbacks:
            segment_avg = sum(f.rating for f in segment_feedbacks) / len(segment_feedbacks)
        else:
            segment_avg = 0
        recent_trend[f"segment_{i+1}"] = segment_avg
    
    return {
        "total_feedbacks": total,
        "average_rating": avg_rating,
        "rating_distribution": rating_distribution,
        "recent_trend": recent_trend
    }


# CRUD pour ModelMetrics
def create_model_metrics(db: Session, metrics: ModelMetricsCreate) -> ModelMetrics:
    """Crée de nouvelles métriques pour un modèle"""
    db_metrics = ModelMetrics(
        model_version=metrics.model_version,
        model_type=metrics.model_type,
        accuracy=metrics.accuracy,
        precision=metrics.precision,
        recall=metrics.recall,
        f1_score=metrics.f1_score,
        auc_roc=metrics.auc_roc,
        avg_satisfaction=metrics.avg_satisfaction,
        conversion_rate=metrics.conversion_rate,
        dataset_size=metrics.dataset_size,
        is_deployed=metrics.is_deployed,
        model_config=metrics.model_config
    )
    db.add(db_metrics)
    db.commit()
    db.refresh(db_metrics)
    return db_metrics


def get_model_metrics(db: Session, metrics_id: int) -> Optional[ModelMetrics]:
    """Récupère des métriques par leur ID"""
    return db.query(ModelMetrics).filter(ModelMetrics.id == metrics_id).first()


def get_latest_model_metrics(db: Session, model_type: str) -> Optional[ModelMetrics]:
    """Récupère les dernières métriques pour un type de modèle"""
    return db.query(ModelMetrics).filter(
        ModelMetrics.model_type == model_type
    ).order_by(ModelMetrics.training_date.desc()).first()


def get_deployed_model_metrics(db: Session, model_type: str) -> Optional[ModelMetrics]:
    """Récupère les métriques du modèle déployé pour un type donné"""
    return db.query(ModelMetrics).filter(
        ModelMetrics.model_type == model_type,
        ModelMetrics.is_deployed == True
    ).first()


def deploy_model(db: Session, model_version: str, model_type: str) -> bool:
    """Déploie un modèle (définit is_deployed=True pour cette version et False pour les autres)"""
    # Désactiver tous les modèles déployés du même type
    db.query(ModelMetrics).filter(
        ModelMetrics.model_type == model_type,
        ModelMetrics.is_deployed == True
    ).update({"is_deployed": False})
    
    # Activer le nouveau modèle
    result = db.query(ModelMetrics).filter(
        ModelMetrics.model_version == model_version,
        ModelMetrics.model_type == model_type
    ).update({"is_deployed": True})
    
    db.commit()
    return result > 0


# CRUD pour FeedbackAlert
def create_feedback_alert(db: Session, alert: FeedbackAlertCreate) -> FeedbackAlert:
    """Crée une nouvelle alerte de feedback"""
    db_alert = FeedbackAlert(
        alert_type=alert.alert_type,
        severity=alert.severity,
        message=alert.message,
        details=alert.details
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert


def get_feedback_alert(db: Session, alert_id: int) -> Optional[FeedbackAlert]:
    """Récupère une alerte par son ID"""
    return db.query(FeedbackAlert).filter(FeedbackAlert.id == alert_id).first()


def get_active_alerts(db: Session) -> List[FeedbackAlert]:
    """Récupère toutes les alertes actives (non résolues)"""
    return db.query(FeedbackAlert).filter(FeedbackAlert.resolved == False).all()


def resolve_alert(db: Session, alert_id: int, resolved_by: str) -> bool:
    """Marque une alerte comme résolue"""
    result = db.query(FeedbackAlert).filter(
        FeedbackAlert.id == alert_id
    ).update({
        "resolved": True,
        "resolved_at": datetime.now(),
        "resolved_by": resolved_by
    })
    db.commit()
    return result > 0
