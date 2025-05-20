from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from ..tracking.schema import FeedbackRating
from ..tracking.collector import EventCollector
from ..tracking.privacy import PrivacyManager
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/feedback", tags=["feedback"])

class MatchFeedbackRequest(BaseModel):
    match_id: str
    user_id: str
    rating: FeedbackRating
    feedback_text: Optional[str] = None
    specific_aspects: Dict[str, int] = {}

class RecommendationFeedbackRequest(BaseModel):
    match_id: str
    user_id: str
    is_relevant: bool
    is_timely: bool
    would_recommend: bool
    comments: Optional[str] = None

# Dépendance pour obtenir le collecteur d'événements
def get_event_collector() -> EventCollector:
    privacy_manager = PrivacyManager()  # En pratique, ceci serait un singleton
    return EventCollector(privacy_manager)

@router.post("/match", status_code=201)
async def submit_match_feedback(
    feedback: MatchFeedbackRequest,
    collector: EventCollector = Depends(get_event_collector)
):
    """Soumettre un feedback sur un match"""
    from ..tracking.schema import MatchFeedbackEvent, EventType
    
    # Créer un événement de feedback
    event = MatchFeedbackEvent(
        user_id=feedback.user_id,
        match_id=feedback.match_id,
        rating=feedback.rating,
        feedback_text=feedback.feedback_text,
        specific_aspects=feedback.specific_aspects
    )
    
    # Collecter l'événement
    success = await collector.collect_event(event)
    if not success:
        raise HTTPException(status_code=403, detail="Consent required for feedback collection")
    
    return {"status": "feedback_recorded", "feedback_id": event.event_id}

@router.post("/recommendation", status_code=201)
async def submit_recommendation_feedback(
    feedback: RecommendationFeedbackRequest,
    collector: EventCollector = Depends(get_event_collector)
):
    """Soumettre un feedback sur la qualité d'une recommandation"""
    from ..tracking.schema import MatchFeedbackEvent, EventType
    
    # Convertir les booléens en valeurs numériques (1-5)
    relevance_score = 5 if feedback.is_relevant else 1
    timeliness_score = 5 if feedback.is_timely else 1
    recommendation_score = 5 if feedback.would_recommend else 1
    
    # Calculer un score moyen
    avg_rating = (relevance_score + timeliness_score + recommendation_score) / 3
    rating = FeedbackRating(round(avg_rating))
    
    # Créer un événement de feedback structuré
    event = MatchFeedbackEvent(
        user_id=feedback.user_id,
        match_id=feedback.match_id,
        rating=rating,
        feedback_text=feedback.comments,
        specific_aspects={
            "relevance": relevance_score,
            "timeliness": timeliness_score,
            "recommendation": recommendation_score
        }
    )
    
    # Collecter l'événement
    success = await collector.collect_event(event)
    if not success:
        raise HTTPException(status_code=403, detail="Consent required for feedback collection")
    
    return {"status": "feedback_recorded", "feedback_id": event.event_id}