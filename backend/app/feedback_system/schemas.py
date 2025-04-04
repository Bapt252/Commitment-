from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime


class MatchingFeedbackBase(BaseModel):
    """Modèle de base pour le feedback de matching"""
    matching_id: int
    user_id: int
    rating: int = Field(ge=1, le=5, description="Note de 1 à 5")
    comment: Optional[str] = None
    interaction_happened: bool = False


class MatchingFeedbackCreate(MatchingFeedbackBase):
    """Modèle pour la création d'un feedback de matching"""
    time_to_first_message: Optional[int] = None
    message_count: Optional[int] = None
    engagement_duration: Optional[int] = None


class MatchingFeedbackInDB(MatchingFeedbackBase):
    """Modèle pour un feedback stocké en base de données"""
    id: int
    feedback_date: datetime
    time_to_first_message: Optional[int] = None
    message_count: int = 0
    engagement_duration: Optional[int] = None

    class Config:
        orm_mode = True


class MatchingFeedbackResponse(MatchingFeedbackInDB):
    """Modèle de réponse pour un feedback"""
    pass


class ModelMetricsBase(BaseModel):
    """Modèle de base pour les métriques de modèle"""
    model_version: str
    model_type: str
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    auc_roc: Optional[float] = None
    avg_satisfaction: Optional[float] = None
    conversion_rate: Optional[float] = None
    dataset_size: int
    is_deployed: bool = False
    model_config: Optional[Dict[str, Any]] = None


class ModelMetricsCreate(ModelMetricsBase):
    """Modèle pour la création des métriques de modèle"""
    pass


class ModelMetricsInDB(ModelMetricsBase):
    """Modèle pour les métriques stockées en base de données"""
    id: int
    training_date: datetime

    class Config:
        orm_mode = True


class ModelMetricsResponse(ModelMetricsInDB):
    """Modèle de réponse pour les métriques de modèle"""
    pass


class FeedbackAlertBase(BaseModel):
    """Modèle de base pour les alertes de feedback"""
    alert_type: str
    severity: str
    message: str
    details: Optional[str] = None


class FeedbackAlertCreate(FeedbackAlertBase):
    """Modèle pour la création d'une alerte de feedback"""
    pass


class FeedbackAlertInDB(FeedbackAlertBase):
    """Modèle pour une alerte stockée en base de données"""
    id: int
    created_at: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None

    class Config:
        orm_mode = True


class FeedbackAlertResponse(FeedbackAlertInDB):
    """Modèle de réponse pour une alerte de feedback"""
    pass


class FeedbackStats(BaseModel):
    """Statistiques de feedback"""
    total_feedbacks: int
    average_rating: float
    rating_distribution: Dict[int, int]
    recent_trend: Dict[str, float]
    engagement_metrics: Dict[str, Any]


class ModelPerformance(BaseModel):
    """Performance d'un modèle dans le temps"""
    model_versions: List[str]
    training_dates: List[datetime]
    metrics: Dict[str, List[float]]
    is_deployed: List[bool]


class SystemHealthResponse(BaseModel):
    """Réponse sur l'état de santé du système"""
    status: str
    models_status: Dict[str, str]
    active_alerts: List[FeedbackAlertResponse]
    recent_metrics: Dict[str, float]
    last_training: datetime
    feedback_count_last_7_days: int
