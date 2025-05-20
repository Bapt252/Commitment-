from enum import Enum
from typing import Dict, List, Optional, Union, Any
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

class BaseEvent:
    def __init__(self, user_id: str, event_type: EventType, session_id: Optional[str] = None):
        self.event_id = str(uuid.uuid4())
        self.user_id = user_id
        self.timestamp = datetime.utcnow()
        self.event_type = event_type
        self.session_id = session_id
    
    def to_dict(self):
        return {
            "event_id": self.event_id,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type.value,
            "session_id": self.session_id
        }
    
class MatchProposedEvent(BaseEvent):
    def __init__(self, user_id: str, match_id: str, match_score: float, 
                 match_parameters: Dict[str, Any], alternatives_count: int,
                 constraint_satisfaction: Dict[str, float], session_id: Optional[str] = None):
        super().__init__(user_id, EventType.MATCH_PROPOSED, session_id)
        self.match_id = match_id
        self.match_score = match_score
        self.match_parameters = match_parameters
        self.alternatives_count = alternatives_count
        self.constraint_satisfaction = constraint_satisfaction
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            "match_id": self.match_id,
            "match_score": self.match_score,
            "match_parameters": self.match_parameters,
            "alternatives_count": self.alternatives_count,
            "constraint_satisfaction": self.constraint_satisfaction
        })
        return data

class MatchViewedEvent(BaseEvent):
    def __init__(self, user_id: str, match_id: str, view_duration_seconds: float,
                 view_complete: bool, session_id: Optional[str] = None):
        super().__init__(user_id, EventType.MATCH_VIEWED, session_id)
        self.match_id = match_id
        self.view_duration_seconds = view_duration_seconds
        self.view_complete = view_complete
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            "match_id": self.match_id,
            "view_duration_seconds": self.view_duration_seconds,
            "view_complete": self.view_complete
        })
        return data

class MatchDecisionEvent(BaseEvent):
    def __init__(self, user_id: str, match_id: str, decision: bool, 
                 decision_time_seconds: float, reasons: Optional[List[str]] = None,
                 session_id: Optional[str] = None):
        event_type = EventType.MATCH_ACCEPTED if decision else EventType.MATCH_REJECTED
        super().__init__(user_id, event_type, session_id)
        self.match_id = match_id
        self.decision_time_seconds = decision_time_seconds
        self.reasons = reasons or []
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            "match_id": self.match_id,
            "decision_time_seconds": self.decision_time_seconds,
            "reasons": self.reasons
        })
        return data

class MatchFeedbackEvent(BaseEvent):
    def __init__(self, user_id: str, match_id: str, rating: FeedbackRating,
                 feedback_text: Optional[str] = None, specific_aspects: Dict[str, int] = None,
                 session_id: Optional[str] = None):
        super().__init__(user_id, EventType.MATCH_FEEDBACK, session_id)
        self.match_id = match_id
        self.rating = rating
        self.feedback_text = feedback_text
        self.specific_aspects = specific_aspects or {}
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            "match_id": self.match_id,
            "rating": self.rating.value,
            "feedback_text": self.feedback_text,
            "specific_aspects": self.specific_aspects
        })
        return data

class MatchCompletionEvent(BaseEvent):
    def __init__(self, user_id: str, match_id: str, completed: bool, duration_days: float,
                 completion_rate: float, success_indicators: Dict[str, float] = None,
                 session_id: Optional[str] = None):
        event_type = EventType.MATCH_COMPLETED if completed else EventType.MATCH_ABANDONED
        super().__init__(user_id, event_type, session_id)
        self.match_id = match_id
        self.duration_days = duration_days
        self.completion_rate = completion_rate
        self.success_indicators = success_indicators or {}
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            "match_id": self.match_id,
            "duration_days": self.duration_days,
            "completion_rate": self.completion_rate,
            "success_indicators": self.success_indicators
        })
        return data