from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Dict, List, Optional, Any
import hashlib
from ..tracking.schema import EventType, FeedbackRating, BaseEvent, MatchProposedEvent, MatchViewedEvent, MatchDecisionEvent, MatchFeedbackEvent
from ..tracking.collector import EventCollector
from ..tracking.privacy import PrivacyManager, ConsentOptions

# Initialiser les singletons
privacy_manager = PrivacyManager()
event_collector = EventCollector(privacy_manager)

# Créer le router API
router = APIRouter(prefix="/api/tracking", tags=["tracking"])


@router.post("/consent")
async def record_consent(request: Request, user_id: str, 
                       analytics: bool = False, preferences: bool = False, improvement: bool = False):
    """Enregistre le consentement utilisateur"""
    # Hacher l'IP pour l'audit (mais ne pas la stocker en clair)
    client_ip = request.client.host if request.client else None
    ip_hash = None
    if client_ip:
        ip_hash = hashlib.sha256(client_ip.encode()).hexdigest()
    
    options = ConsentOptions(analytics=analytics, preferences=preferences, improvement=improvement)
    consent_id = privacy_manager.record_consent(user_id, options, ip_hash)
    
    return {
        "status": "success",
        "consent_id": consent_id,
        "options": options.to_dict()
    }


@router.get("/consent/{user_id}")
async def get_consent_status(user_id: str):
    """Obtient le statut actuel du consentement utilisateur"""
    consent = privacy_manager._get_consent_from_db(user_id)
    
    if not consent:
        raise HTTPException(status_code=404, detail="No consent record found")
    
    return {
        "status": "success",
        "options": consent.to_dict()
    }


@router.post("/event/match-proposed")
async def track_match_proposed(
    user_id: str, match_id: str, match_score: float,
    match_parameters: Dict[str, Any], alternatives_count: int,
    constraint_satisfaction: Dict[str, float], session_id: Optional[str] = None
):
    """Enregistre un événement de match proposé"""
    event = MatchProposedEvent(
        user_id=user_id,
        match_id=match_id,
        match_score=match_score,
        match_parameters=match_parameters,
        alternatives_count=alternatives_count,
        constraint_satisfaction=constraint_satisfaction,
        session_id=session_id
    )
    
    success = event_collector.collect_event(event)
    if not success:
        raise HTTPException(status_code=403, detail="Consent required for tracking")
    
    return {"status": "success", "event_id": event.event_id}


@router.post("/event/match-viewed")
async def track_match_viewed(
    user_id: str, match_id: str, view_duration_seconds: float,
    view_complete: bool, session_id: Optional[str] = None
):
    """Enregistre un événement de visualisation de match"""
    event = MatchViewedEvent(
        user_id=user_id,
        match_id=match_id,
        view_duration_seconds=view_duration_seconds,
        view_complete=view_complete,
        session_id=session_id
    )
    
    success = event_collector.collect_event(event)
    if not success:
        raise HTTPException(status_code=403, detail="Consent required for tracking")
    
    return {"status": "success", "event_id": event.event_id}


@router.post("/event/match-decision")
async def track_match_decision(
    user_id: str, match_id: str, decision: bool,
    decision_time_seconds: float, reasons: Optional[List[str]] = None,
    session_id: Optional[str] = None
):
    """Enregistre un événement de décision (acceptation/rejet) de match"""
    event = MatchDecisionEvent(
        user_id=user_id,
        match_id=match_id,
        decision=decision,
        decision_time_seconds=decision_time_seconds,
        reasons=reasons,
        session_id=session_id
    )
    
    success = event_collector.collect_event(event)
    if not success:
        raise HTTPException(status_code=403, detail="Consent required for tracking")
    
    return {"status": "success", "event_id": event.event_id}


@router.post("/event/match-feedback")
async def track_match_feedback(
    user_id: str, match_id: str, rating: int,
    feedback_text: Optional[str] = None, specific_aspects: Dict[str, int] = None,
    session_id: Optional[str] = None
):
    """Enregistre un événement de feedback sur un match"""
    try:
        rating_enum = FeedbackRating(rating)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid rating value (must be 1-5)")
    
    event = MatchFeedbackEvent(
        user_id=user_id,
        match_id=match_id,
        rating=rating_enum,
        feedback_text=feedback_text,
        specific_aspects=specific_aspects or {},
        session_id=session_id
    )
    
    success = event_collector.collect_event(event)
    if not success:
        raise HTTPException(status_code=403, detail="Consent required for tracking")
    
    return {"status": "success", "event_id": event.event_id}