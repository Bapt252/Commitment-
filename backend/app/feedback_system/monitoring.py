from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging
from datetime import datetime, timedelta

from app.core.database import get_db
from app.feedback_system.schemas import (
    ModelMetricsResponse,
    FeedbackAlertResponse,
    SystemHealthResponse
)
from app.feedback_system.crud import (
    get_active_alerts,
    get_recent_feedbacks,
    get_latest_model_metrics,
    get_deployed_model_metrics,
    resolve_alert,
    create_feedback_alert
)
from app.feedback_system.schemas import FeedbackAlertCreate

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health", response_model=SystemHealthResponse)
async def get_system_health(db: Session = Depends(get_db)):
    """Récupère l'état de santé général du système"""
    # Vérifier les modèles déployés
    matching_model = get_deployed_model_metrics(db, "matching")
    # Ajouter d'autres modèles si nécessaire
    
    # Vérifier les alertes actives
    active_alerts = get_active_alerts(db)
    
    # Calculer les métriques récentes
    recent_feedbacks = get_recent_feedbacks(db, days=7)
    recent_metrics = {
        "avg_rating": sum(f.rating for f in recent_feedbacks) / len(recent_feedbacks) if recent_feedbacks else 0,
        "feedback_count": len(recent_feedbacks)
    }
    
    # Déterminer le statut global
    if not matching_model:
        status = "critical"
    elif active_alerts and any(a.severity == "critical" for a in active_alerts):
        status = "warning"
    else:
        status = "healthy"
    
    return {
        "status": status,
        "models_status": {
            "matching": "deployed" if matching_model else "missing"
        },
        "active_alerts": active_alerts,
        "recent_metrics": recent_metrics,
        "last_training": matching_model.training_date if matching_model else datetime.min,
        "feedback_count_last_7_days": len(recent_feedbacks)
    }

@router.get("/models/{model_type}", response_model=List[ModelMetricsResponse])
async def get_model_history(
    model_type: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Récupère l'historique des performances du modèle"""
    # Dans une implémentation réelle, vous récupéreriez l'historique complet des modèles
    # Exemple simplifié avec le dernier modèle uniquement
    latest_model = get_latest_model_metrics(db, model_type)
    if not latest_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aucun modèle trouvé pour le type {model_type}"
        )
    
    return [latest_model]

@router.get("/alerts", response_model=List[FeedbackAlertResponse])
async def get_alerts(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Récupère les alertes du système"""
    if active_only:
        return get_active_alerts(db)
    
    # Dans une implémentation réelle, vous récupéreriez toutes les alertes
    return get_active_alerts(db)  # Simplifié pour l'exemple

@router.post("/alerts/{alert_id}/resolve", response_model=FeedbackAlertResponse)
async def resolve_alert_endpoint(
    alert_id: int,
    resolved_by: str,
    db: Session = Depends(get_db)
):
    """Marque une alerte comme résolue"""
    success = resolve_alert(db, alert_id, resolved_by)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alerte {alert_id} non trouvée"
        )
    
    # Récupérer l'alerte mise à jour
    updated_alert = db.query(FeedbackAlert).filter(FeedbackAlert.id == alert_id).first()
    return updated_alert

@router.post("/check-alerts", status_code=status.HTTP_200_OK)
async def check_system_alerts(db: Session = Depends(get_db)):
    """Vérifie les conditions d'alerte et crée des alertes si nécessaire"""
    alerts_created = []
    
    # 1. Vérifier la baisse de performance des ratings
    try:
        alerts_created.extend(check_rating_drops(db))
    except Exception as e:
        logger.error(f"Erreur lors de la vérification des baisses de ratings: {str(e)}")
    
    # 2. Vérifier le taux de feedbacks négatifs
    try:
        alerts_created.extend(check_negative_feedback_rate(db))
    except Exception as e:
        logger.error(f"Erreur lors de la vérification du taux de feedbacks négatifs: {str(e)}")
    
    # 3. Vérifier le temps écoulé depuis le dernier entraînement
    try:
        alerts_created.extend(check_training_freshness(db))
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de la fraîcheur de l'entraînement: {str(e)}")
    
    return {
        "checked_at": datetime.now().isoformat(),
        "alerts_created": len(alerts_created),
        "alerts": alerts_created
    }

def check_rating_drops(db: Session) -> List[Dict[str, Any]]:
    """Vérifie si les ratings ont chuté récemment"""
    alerts_created = []
    
    # Comparer les ratings des 7 derniers jours avec les 7 jours précédents
    recent = get_recent_feedbacks(db, days=7)
    previous = get_recent_feedbacks(db, days=14)  # Les 14 derniers jours
    previous = [f for f in previous if f.feedback_date < datetime.now() - timedelta(days=7)]  # Filtrer les 7j précédents
    
    if not recent or not previous:
        return alerts_created
    
    recent_avg = sum(f.rating for f in recent) / len(recent)
    previous_avg = sum(f.rating for f in previous) / len(previous)
    
    # Si la baisse est de plus de 10%
    if recent_avg < previous_avg * 0.9:
        alert = FeedbackAlertCreate(
            alert_type="rating_drop",
            severity="warning",
            message="Baisse significative des ratings",
            details=f"Les ratings moyens ont chuté de {previous_avg:.2f} à {recent_avg:.2f} (-{(1-recent_avg/previous_avg)*100:.1f}%)"
        )
        db_alert = create_feedback_alert(db, alert)
        alerts_created.append({
            "id": db_alert.id,
            "alert_type": db_alert.alert_type,
            "severity": db_alert.severity,
            "message": db_alert.message
        })
    
    return alerts_created

def check_negative_feedback_rate(db: Session) -> List[Dict[str, Any]]:
    """Vérifie si le taux de feedbacks négatifs est anormalement élevé"""
    alerts_created = []
    
    # Analyser les feedbacks des 3 derniers jours
    recent = get_recent_feedbacks(db, days=3)
    
    if not recent:
        return alerts_created
    
    # Compter les feedbacks négatifs (rating <= 2)
    negative = [f for f in recent if f.rating <= 2]
    negative_rate = len(negative) / len(recent)
    
    # Si plus de 30% sont négatifs
    if negative_rate > 0.3:
        alert = FeedbackAlertCreate(
            alert_type="high_negative_rate",
            severity="critical" if negative_rate > 0.5 else "warning",
            message="Taux élevé de feedbacks négatifs",
            details=f"{len(negative)} feedbacks négatifs sur {len(recent)} ({negative_rate*100:.1f}%)"
        )
        db_alert = create_feedback_alert(db, alert)
        alerts_created.append({
            "id": db_alert.id,
            "alert_type": db_alert.alert_type,
            "severity": db_alert.severity,
            "message": db_alert.message
        })
    
    return alerts_created

def check_training_freshness(db: Session) -> List[Dict[str, Any]]:
    """Vérifie si le modèle n'a pas été réentraîné depuis longtemps"""
    alerts_created = []
    
    # Vérifier le dernier entraînement du modèle de matching
    latest_model = get_latest_model_metrics(db, "matching")
    
    if not latest_model:
        alert = FeedbackAlertCreate(
            alert_type="no_model",
            severity="critical",
            message="Aucun modèle de matching trouvé",
            details="Aucun modèle de matching n'a été entraîné. Veuillez lancer un entraînement initial."
        )
        db_alert = create_feedback_alert(db, alert)
        alerts_created.append({
            "id": db_alert.id,
            "alert_type": db_alert.alert_type,
            "severity": db_alert.severity,
            "message": db_alert.message
        })
        return alerts_created
    
    # Vérifier si le modèle a plus de 30 jours
    if latest_model.training_date < datetime.now() - timedelta(days=30):
        days_old = (datetime.now() - latest_model.training_date).days
        alert = FeedbackAlertCreate(
            alert_type="old_model",
            severity="warning",
            message="Modèle de matching obsolète",
            details=f"Le modèle de matching a {days_old} jours. Considérez un réentraînement."
        )
        db_alert = create_feedback_alert(db, alert)
        alerts_created.append({
            "id": db_alert.id,
            "alert_type": db_alert.alert_type,
            "severity": db_alert.severity,
            "message": db_alert.message
        })
    
    return alerts_created
