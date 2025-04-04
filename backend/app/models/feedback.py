from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class FeedbackType(str, Enum):
    """Types d'entités qui peuvent recevoir du feedback"""
    JOB_PARSING = "job_parsing"
    MATCHING = "matching"
    QUESTIONNAIRE = "questionnaire"


class FeedbackBase(BaseModel):
    """Modèle de base pour le feedback"""
    entity_type: FeedbackType
    entity_id: int
    rating: int = Field(ge=1, le=5, description="Note de 1 à 5")
    comments: Optional[str] = None
    aspects: Dict[str, int] = Field(default_factory=dict, description="Notes détaillées par aspect")
    submitted_by: Optional[str] = None


class FeedbackCreate(FeedbackBase):
    """Modèle pour la création d'un feedback"""
    pass


class FeedbackInDB(FeedbackBase):
    """Modèle pour un feedback stocké en base de données"""
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class FeedbackResponse(FeedbackInDB):
    """Modèle de réponse pour un feedback"""
    pass


class FeedbackBatchCreate(BaseModel):
    """Modèle pour la création de plusieurs feedbacks en une seule requête"""
    feedbacks: List[FeedbackCreate]


class FeedbackBatchResponse(BaseModel):
    """Modèle de réponse pour une création par lot de feedbacks"""
    total: int
    successful: int
    failed: int
    results: List[FeedbackResponse]
    errors: Optional[List[Dict[str, Any]]] = None


class FeedbackAnalytics(BaseModel):
    """Statistiques d'un type de feedback"""
    count: int
    average_rating: float
    rating_distribution: Dict[int, int] = Field(description="Nombre de feedbacks par note")


class FeedbackStats(BaseModel):
    """Statistiques globales des feedbacks"""
    total_feedbacks: int
    average_rating: float
    by_entity_type: Dict[str, FeedbackAnalytics]
    trend: Dict[str, Any] = Field(description="Évolution des notes dans le temps")
    most_common_issues: Optional[List[Dict[str, Any]]] = None


class FeedbackFilter(BaseModel):
    """Filtres pour la recherche de feedbacks"""
    entity_type: Optional[FeedbackType] = None
    entity_id: Optional[int] = None
    min_rating: Optional[int] = None
    max_rating: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    submitted_by: Optional[str] = None
    page: int = 1
    per_page: int = 10
