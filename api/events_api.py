from fastapi import APIRouter, HTTPException, Depends, Body, Query, Header
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from ..tracking.schema import (
    BaseEvent, MatchProposedEvent, MatchViewedEvent, 
    MatchDecisionEvent, MatchFeedbackEvent
)
from ..tracking.collector import EventCollector
from ..tracking.privacy import PrivacyManager

router = APIRouter(prefix="/api/events", tags=["events"])

# Dépendance pour obtenir le collecteur d'événements
def get_event_collector() -> EventCollector:
    privacy_manager = PrivacyManager()  # En pratique, ceci serait un singleton
    return EventCollector(privacy_manager)

@router.post("/track", status_code=202)
async def track_event(
    event: BaseEvent,
    collector: EventCollector = Depends(get_event_collector),
    user_agent: Optional[str] = Header(None)
):
    """Endpoint générique pour tracker tout type d'événement"""
    success = await collector.collect_event(event)
    if not success:
        raise HTTPException(status_code=403, detail="Consent required for tracking")
    return {"status": "accepted"}

@router.post("/match/proposed", status_code=202)
async def track_match_proposed(
    event: MatchProposedEvent,
    collector: EventCollector = Depends(get_event_collector)
):
    """Tracker qu'un match a été proposé à l'utilisateur"""
    success = await collector.collect_event(event)
    if not success:
        raise HTTPException(status_code=403, detail="Consent required for tracking")
    return {"status": "accepted", "match_id": event.match_id}

@router.post("/match/viewed", status_code=202)
async def track_match_viewed(
    event: MatchViewedEvent,
    collector: EventCollector = Depends(get_event_collector)
):
    """Tracker qu'un match a été visualisé"""
    success = await collector.collect_event(event)
    if not success:
        raise HTTPException(status_code=403, detail="Consent required for tracking")
    return {"status": "accepted"}

@router.post("/match/decision", status_code=202)
async def track_match_decision(
    event: MatchDecisionEvent,
    collector: EventCollector = Depends(get_event_collector)
):
    """Tracker la décision de l'utilisateur (acceptation/refus)"""
    success = await collector.collect_event(event)
    if not success:
        raise HTTPException(status_code=403, detail="Consent required for tracking")
    return {"status": "accepted"}

@router.post("/match/feedback", status_code=202)
async def track_match_feedback(
    event: MatchFeedbackEvent,
    collector: EventCollector = Depends(get_event_collector)
):
    """Collecter le feedback explicite sur un match"""
    success = await collector.collect_event(event)
    if not success:
        raise HTTPException(status_code=403, detail="Consent required for tracking")
    return {"status": "accepted"}