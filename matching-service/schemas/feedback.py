from pydantic import BaseModel, Field, validator, UUID4
from datetime import datetime
from typing import Optional, Literal
from enum import Enum


class MatchQualityEnum(str, Enum):
    VERY_GOOD = "très bon"
    GOOD = "bon"
    MEDIUM = "moyen"
    POOR = "faible"
    UNACCEPTABLE = "inacceptable"


class FeedbackBase(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Note de 1 à 5")
    match_quality: MatchQualityEnum
    comment: Optional[str] = Field(None, max_length=1000, description="Commentaire optionnel")


class FeedbackCreate(FeedbackBase):
    match_id: UUID4
    
    @validator('comment')
    def clean_comment(cls, v):
        if v:
            return v.strip()
        return v


class FeedbackResponse(FeedbackBase):
    id: UUID4
    match_id: UUID4
    user_id: UUID4
    user_type: Literal["recruiter", "candidate"]
    algorithm_version: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class FeedbackStats(BaseModel):
    average_rating: float
    total_feedbacks: int
    quality_distribution: dict[MatchQualityEnum, int]
    latest_feedback_date: Optional[datetime]