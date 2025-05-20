from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union, Any
from enum import Enum
from datetime import datetime
import uuid

class EventType(str, Enum):
    MATCH_PROPOSED = "match_proposed"         # Un match est proposé à l'utilisateur
    MATCH_VIEWED = "match_viewed"             # L'utilisateur a vu le match proposé
    MATCH_ACCEPTED = "match_accepted"         # L'utilisateur a accepté le match
    MATCH_REJECTED = "match_rejected"         # L'utilisateur a refusé le match
    MATCH_FEEDBACK = "match_feedback"         # L'utilisateur a donné un feedback explicite
    MATCH_INTERACTION = "match_interaction"   # Interaction après le match
    MATCH_COMPLETED = "match_completed"       # Engagement terminé avec succès
    MATCH_ABANDONED = "match_abandoned"       # Engagement abandonné avant terme

class FeedbackRating(int, Enum):
    VERY_BAD = 1
    BAD = 2
    NEUTRAL = 3
    GOOD = 4
    VERY_GOOD = 5

class BaseEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str  # Identifiant anonymisé de l'utilisateur
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    event_type: EventType
    session_id: Optional[str] = None
    
class MatchProposedEvent(BaseEvent):
    event_type: EventType = EventType.MATCH_PROPOSED
    match_id: str
    match_score: float
    match_parameters: Dict[str, Any]  # Paramètres utilisés pour ce match
    alternatives_count: int  # Nombre d'alternatives considérées
    constraint_satisfaction: Dict[str, float]  # Niveau de satisfaction des contraintes

class MatchViewedEvent(BaseEvent):
    event_type: EventType = EventType.MATCH_VIEWED
    match_id: str
    view_duration_seconds: float
    view_complete: bool  # Si l'utilisateur a vu toutes les infos du match

class MatchDecisionEvent(BaseEvent):
    event_type: Union[EventType.MATCH_ACCEPTED, EventType.MATCH_REJECTED]
    match_id: str
    decision_time_seconds: float  # Temps pris pour décider
    reasons: Optional[List[str]] = None  # Raisons données par l'utilisateur

class MatchFeedbackEvent(BaseEvent):
    event_type: EventType = EventType.MATCH_FEEDBACK
    match_id: str
    rating: FeedbackRating
    feedback_text: Optional[str] = None
    specific_aspects: Dict[str, int] = {}  # Notation par aspect (ex: pertinence=4, timing=3)

class MatchInteractionEvent(BaseEvent):
    event_type: EventType = EventType.MATCH_INTERACTION
    match_id: str
    interaction_type: str  # Type d'interaction (message, activité, etc.)
    interaction_count: int  # Nombre d'interactions dans cette session
    
class MatchCompletionEvent(BaseEvent):
    event_type: Union[EventType.MATCH_COMPLETED, EventType.MATCH_ABANDONED] 
    match_id: str
    duration_days: float  # Durée de l'engagement en jours
    completion_rate: float  # 0-1, niveau d'achèvement des objectifs
    success_indicators: Dict[str, float]  # Indicateurs objectifs de succès