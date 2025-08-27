from typing import Dict, Optional, Literal
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from models.feedback import MatchFeedback, MatchQualityEnum
from models.match_result import MatchResult
from schemas.feedback import FeedbackCreate, FeedbackResponse
from config import get_algorithm_version
import logging

logger = logging.getLogger(__name__)


class FeedbackService:
    def __init__(self, db: Session):
        self.db = db
        self.algorithm_version = get_algorithm_version()

    async def save_feedback(
        self, 
        match_id: UUID, 
        user_id: UUID, 
        user_type: Literal["recruiter", "candidate"], 
        payload: FeedbackCreate
    ) -> FeedbackResponse:
        """Enregistre un feedback utilisateur pour un matching."""
        try:
            # Vérifier que le match existe
            match_result = self.db.query(MatchResult).filter(
                MatchResult.id == match_id
            ).first()
            
            if not match_result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Match with ID {match_id} not found"
                )
            
            # Vérifier que l'utilisateur n'a pas déjà donné un feedback
            existing_feedback = self.db.query(MatchFeedback).filter(
                MatchFeedback.match_id == match_id,
                MatchFeedback.user_id == user_id
            ).first()
            
            if existing_feedback:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Feedback already exists for this match and user"
                )
            
            # Créer le feedback
            feedback = MatchFeedback(
                match_id=match_id,
                user_id=user_id,
                user_type=user_type,
                rating=payload.rating,
                match_quality=payload.match_quality,
                comment=payload.comment,
                algorithm_version=self.algorithm_version
            )
            
            self.db.add(feedback)
            self.db.commit()
            self.db.refresh(feedback)
            
            logger.info(f"Feedback saved successfully: {feedback.id}")
            return FeedbackResponse.from_orm(feedback)
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Database integrity error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid feedback data"
            )
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving feedback: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save feedback"
            )

    async def get_feedback_stats(self, match_id: Optional[UUID] = None) -> Dict:
        """Récupère les statistiques des feedbacks."""
        query = self.db.query(MatchFeedback)
        
        if match_id:
            query = query.filter(MatchFeedback.match_id == match_id)
        
        feedbacks = query.all()
        
        if not feedbacks:
            return {
                "average_rating": 0.0,
                "total_feedbacks": 0,
                "quality_distribution": {},
                "latest_feedback_date": None
            }
        
        total_rating = sum(f.rating for f in feedbacks)
        quality_distribution = {}
        
        for quality in MatchQualityEnum:
            count = len([f for f in feedbacks if f.match_quality == quality])
            quality_distribution[quality.value] = count
        
        return {
            "average_rating": round(total_rating / len(feedbacks), 2),
            "total_feedbacks": len(feedbacks),
            "quality_distribution": quality_distribution,
            "latest_feedback_date": max(f.created_at for f in feedbacks) if feedbacks else None
        }

    async def get_feedback_by_user(self, user_id: UUID) -> list[FeedbackResponse]:
        """Récupère tous les feedbacks d'un utilisateur."""
        feedbacks = self.db.query(MatchFeedback).filter(
            MatchFeedback.user_id == user_id
        ).order_by(MatchFeedback.created_at.desc()).all()
        
        return [FeedbackResponse.from_orm(feedback) for feedback in feedbacks]