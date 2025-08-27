from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
from uuid import UUID
from database import get_db
from schemas.feedback import FeedbackCreate, FeedbackResponse, FeedbackStats
from services.feedback_service import FeedbackService
from auth.dependencies import get_current_user
from models.user import User

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def create_feedback(
    payload: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crée un nouveau feedback pour un matching."""
    feedback_service = FeedbackService(db)
    
    # Déterminer le type d'utilisateur (recruteur ou candidat)
    user_type = "recruiter" if current_user.role == "recruiter" else "candidate"
    
    return await feedback_service.save_feedback(
        match_id=payload.match_id,
        user_id=current_user.id,
        user_type=user_type,
        payload=payload
    )


@router.get("/match/{match_id}", response_model=List[FeedbackResponse])
async def get_feedbacks_for_match(
    match_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère tous les feedbacks pour un match spécifique."""
    feedbacks = db.query(MatchFeedback).filter(
        MatchFeedback.match_id == match_id
    ).all()
    
    return [FeedbackResponse.from_orm(feedback) for feedback in feedbacks]


@router.get("/stats/{match_id}", response_model=FeedbackStats)
async def get_match_feedback_stats(
    match_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère les statistiques de feedback pour un match."""
    feedback_service = FeedbackService(db)
    return await feedback_service.get_feedback_stats(match_id)


@router.get("/user/me", response_model=List[FeedbackResponse])
async def get_my_feedbacks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère tous les feedbacks de l'utilisateur connecté."""
    feedback_service = FeedbackService(db)
    return await feedback_service.get_feedback_by_user(current_user.id)