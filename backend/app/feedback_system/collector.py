from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from app.core.database import get_db
from app.feedback_system.schemas import (
    MatchingFeedbackCreate,
    MatchingFeedbackResponse,
    FeedbackStats
)
from app.feedback_system.crud import (
    create_matching_feedback,
    get_matching_feedback,
    get_feedbacks_by_matching,
    get_feedback_stats
)
from app.feedback_system.training import check_threshold_for_retraining

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=MatchingFeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_matching_feedback(
    feedback: MatchingFeedbackCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Soumet un feedback pour un matching"""
    try:
        # Vérifier si le matching existe
        # Note: Dans une implémentation complète, vous devriez vérifier si le matching existe vraiment
        
        # Créer le feedback
        db_feedback = create_matching_feedback(db, feedback)
        
        # Déclencher une vérification pour le réentraînement en arrière-plan
        background_tasks.add_task(check_threshold_for_retraining, db)
        
        return db_feedback
    except Exception as e:
        logger.error(f"Erreur lors de la soumission du feedback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Une erreur est survenue: {str(e)}"
        )

@router.get("/{feedback_id}", response_model=MatchingFeedbackResponse)
async def get_feedback(
    feedback_id: int,
    db: Session = Depends(get_db)
):
    """Récupère un feedback spécifique"""
    feedback = get_matching_feedback(db, feedback_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback non trouvé"
        )
    return feedback

@router.get("/matching/{matching_id}", response_model=List[MatchingFeedbackResponse])
async def get_feedback_by_matching(
    matching_id: int,
    db: Session = Depends(get_db)
):
    """Récupère tous les feedbacks pour un matching donné"""
    return get_feedbacks_by_matching(db, matching_id)

@router.get("/stats", response_model=FeedbackStats)
async def get_stats(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Récupère des statistiques sur les feedbacks"""
    stats = get_feedback_stats(db, days)
    
    # Ajouter des métriques d'engagement fictives (à remplacer par des calculs réels)
    stats["engagement_metrics"] = {
        "avg_time_to_first_message": 120,  # en minutes
        "avg_message_count": 5.3,
        "conversion_rate": 0.68,  # pourcentage de matchings qui ont conduit à un engagement
        "avg_engagement_duration": 14.2  # en jours
    }
    
    return stats
